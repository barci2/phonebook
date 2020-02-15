import attr
import random
import paho.mqtt.client
import requests
from ._common import log, kw_only
from . import _util, _exception, _session, _graphql, _events

from typing import Iterable, Optional


def get_cookie_header(session: requests.Session, url: str) -> str:
    """Extract a cookie header from a requests session."""
    # The cookies are extracted this way to make sure they're escaped correctly
    return requests.cookies.get_cookie_header(
        session.cookies, requests.Request("GET", url),
    )


def generate_session_id() -> int:
    """Generate a random session ID between 1 and 9007199254740991."""
    return random.randint(1, 2 ** 53)


@attr.s(slots=True, kw_only=kw_only, repr=False, eq=False)
class Listener:
    """Helper, to listen for incoming Facebook events."""

    session = attr.ib(type=_session.Session)
    _mqtt = attr.ib(type=paho.mqtt.client.Client)
    _chat_on = attr.ib(type=bool)
    _foreground = attr.ib(type=bool)
    _sequence_id = attr.ib(type=int)
    _sync_token = attr.ib(None, type=str)
    _tmp_events = attr.ib(None, type=Optional[Iterable[_events.Event]])

    _HOST = "edge-chat.facebook.com"

    def __repr__(self) -> str:
        # An alternative repr, to illustrate that you can't create the class directly
        return "<fbchat.Listener session={} chat_on={} foreground={}>".format(
            self.session, self._chat_on, self._foreground
        )

    @classmethod
    def connect(cls, session: _session.Session, chat_on: bool, foreground: bool):
        """Initialize a connection to the Facebook MQTT service.

        Args:
            session: The session to use when making requests.
            chat_on: Whether ...
            foreground: Whether ...

        Example:
            >>> listener = fbchat.Listener.connect(session, chat_on=True, foreground=True)
        """
        mqtt = paho.mqtt.client.Client(
            client_id="mqttwsclient",
            clean_session=True,
            protocol=paho.mqtt.client.MQTTv31,
            transport="websockets",
        )
        mqtt.enable_logger()
        # mqtt.max_inflight_messages_set(20)  # The rest will get queued
        # mqtt.max_queued_messages_set(0)  # Unlimited messages can be queued
        # mqtt.message_retry_set(20)  # Retry sending for at least 20 seconds
        # mqtt.reconnect_delay_set(min_delay=1, max_delay=120)
        # TODO: Is region (lla | atn | odn | others?) important?
        mqtt.tls_set()

        self = cls(
            session=session,
            mqtt=mqtt,
            chat_on=chat_on,
            foreground=foreground,
            sequence_id=cls._fetch_sequence_id(session),
        )

        # Configure callbacks
        mqtt.on_message = self._on_message_handler
        mqtt.on_connect = self._on_connect_handler

        self._configure_connect_options()

        # Attempt to connect
        try:
            rc = mqtt.connect(self._HOST, 443, keepalive=10)
        except (
            # Taken from .loop_forever
            paho.mqtt.client.socket.error,
            OSError,
            paho.mqtt.client.WebsocketConnectionError,
        ) as e:
            raise _exception.FacebookError("MQTT connection failed") from e

        # Raise error if connecting failed
        if rc != paho.mqtt.client.MQTT_ERR_SUCCESS:
            err = paho.mqtt.client.error_string(rc)
            raise _exception.FacebookError("MQTT connection failed: {}".format(err))

        return self

    def _on_message_handler(self, client, userdata, message):
        # Parse payload JSON
        try:
            j = _util.parse_json(message.payload.decode("utf-8"))
        except (_exception.FacebookError, UnicodeDecodeError):
            log.debug(message.payload)
            log.exception("Failed parsing MQTT data on %s as JSON", message.topic)
            return

        log.debug("MQTT payload: %s, %s", message.topic, j)

        if message.topic == "/t_ms":
            # Update sync_token when received
            # This is received in the first message after we've created a messenger
            # sync queue.
            if "syncToken" in j and "firstDeltaSeqId" in j:
                self._sync_token = j["syncToken"]
                self._sequence_id = j["firstDeltaSeqId"]
                return

            if "errorCode" in j:
                error = j["errorCode"]
                # TODO: 'F\xfa\x84\x8c\x85\xf8\xbc-\x88 FB_PAGES_INSUFFICIENT_PERMISSION\x00'
                if error in ("ERROR_QUEUE_NOT_FOUND", "ERROR_QUEUE_OVERFLOW"):
                    # ERROR_QUEUE_NOT_FOUND means that the queue was deleted, since too
                    # much time passed, or that it was simply missing
                    # ERROR_QUEUE_OVERFLOW means that the sequence id was too small, so
                    # the desired events could not be retrieved
                    log.error(
                        "The MQTT listener was disconnected for too long,"
                        " events may have been lost"
                    )
                    self._sync_token = None
                    self._sequence_id = self._fetch_sequence_id(self.session)
                    self._messenger_queue_publish()
                    # TODO: Signal to the user that they should reload their data!
                    return
                log.error("MQTT error code %s received", error)
                return

            # Update last sequence id when received
            if "lastIssuedSeqId" in j:
                self._sequence_id = j["lastIssuedSeqId"]
            else:
                log.error("Missing last sequence id: %s", j)

        try:
            # TODO: Don't handle this in a callback
            self._tmp_events = list(
                _events.parse_events(self.session, message.topic, j)
            )
        except _exception.ParseError:
            log.exception("Failed parsing MQTT data")

    @staticmethod
    def _fetch_sequence_id(session: _session.Session) -> int:
        """Fetch sequence ID."""
        params = {
            "limit": 0,
            "tags": ["INBOX"],
            "before": None,
            "includeDeliveryReceipts": False,
            "includeSeqID": True,
        }
        log.debug("Fetching MQTT sequence ID")
        # Same request as in `Client.fetch_threads`
        (j,) = session._graphql_requests(
            _graphql.from_doc_id("1349387578499440", params)
        )
        try:
            return int(j["viewer"]["message_threads"]["sync_sequence_id"])
        except (KeyError, ValueError) as e:
            raise _exception.ParseError("Could not find sequence id", data=j) from e

    def _on_connect_handler(self, client, userdata, flags, rc):
        if rc == 21:
            raise _exception.FacebookError(
                "Failed connecting. Maybe your cookies are wrong?"
            )
        if rc != 0:
            return  # Don't try to send publish if the connection failed

        self._messenger_queue_publish()

    def _messenger_queue_publish(self):
        # configure receiving messages.
        payload = {
            "sync_api_version": 10,
            "max_deltas_able_to_process": 1000,
            "delta_batch_size": 500,
            "encoding": "JSON",
            "entity_fbid": self.session.user.id,
        }

        # If we don't have a sync_token, create a new messenger queue
        # This is done so that across reconnects, if we've received a sync token, we
        # SHOULD receive a piece of data in /t_ms exactly once!
        if self._sync_token is None:
            topic = "/messenger_sync_create_queue"
            payload["initial_titan_sequence_id"] = str(self._sequence_id)
            payload["device_params"] = None
        else:
            topic = "/messenger_sync_get_diffs"
            payload["last_seq_id"] = str(self._sequence_id)
            payload["sync_token"] = self._sync_token

        self._mqtt.publish(topic, _util.json_minimal(payload), qos=1)

    def _configure_connect_options(self):
        # Generate a new session ID on each reconnect
        session_id = generate_session_id()

        topics = [
            # Things that happen in chats (e.g. messages)
            "/t_ms",
            # Group typing notifications
            "/thread_typing",
            # Private chat typing notifications
            "/orca_typing_notifications",
            # Active notifications
            "/orca_presence",
            # Other notifications not related to chats (e.g. friend requests)
            "/legacy_web",
            # Facebook's continuous error reporting/logging?
            "/br_sr",
            # Response to /br_sr
            "/sr_res",
            # Data about user-to-user calls
            # TODO: Investigate the response from this! (A bunch of binary data)
            # "/t_rtc",
            # TODO: Find out what this does!
            # TODO: Investigate the response from this! (A bunch of binary data)
            # "/t_p",
            # TODO: Find out what this does!
            "/webrtc",
            # TODO: Find out what this does!
            "/onevc",
            # TODO: Find out what this does!
            "/notify_disconnect",
            # Old, no longer active topics
            # These are here just in case something interesting pops up
            "/inbox",
            "/mercury",
            "/messaging_events",
            "/orca_message_notifications",
            "/pp",
            "/webrtc_response",
        ]

        username = {
            # The user ID
            "u": self.session.user.id,
            # Session ID
            "s": session_id,
            # Active status setting
            "chat_on": self._chat_on,
            # foreground_state - Whether the window is focused
            "fg": self._foreground,
            # Can be any random ID
            "d": self.session._client_id,
            # Application ID, taken from facebook.com
            "aid": 219994525426954,
            # MQTT extension by FB, allows making a SUBSCRIBE while CONNECTing
            "st": topics,
            # MQTT extension by FB, allows making a PUBLISH while CONNECTing
            # Using this is more efficient, but the same can be acheived with:
            #     def on_connect(*args):
            #         mqtt.publish(topic, payload, qos=1)
            #     mqtt.on_connect = on_connect
            # TODO: For some reason this doesn't work!
            "pm": [
                # {
                #     "topic": topic,
                #     "payload": payload,
                #     "qos": 1,
                #     "messageId": 65536,
                # }
            ],
            # Unknown parameters
            "cp": 3,
            "ecp": 10,
            "ct": "websocket",
            "mqtt_sid": "",
            "dc": "",
            "no_auto_fg": True,
            "gas": None,
            "pack": [],
        }

        # TODO: Make this thread safe
        self._mqtt.username_pw_set(_util.json_minimal(username))

        headers = {
            # TODO: Make this access thread safe
            "Cookie": get_cookie_header(
                self.session._session, "https://edge-chat.facebook.com/chat"
            ),
            "User-Agent": self.session._session.headers["User-Agent"],
            "Origin": "https://www.facebook.com",
            "Host": self._HOST,
        }

        self._mqtt.ws_set_options(
            path="/chat?sid={}".format(session_id), headers=headers
        )

    def _loop_once(self) -> bool:
        rc = self._mqtt.loop(timeout=1.0)

        # If disconnect() has been called
        # Beware, internal API, may have to change this to something more stable!
        if self._mqtt._state == paho.mqtt.client.mqtt_cs_disconnecting:
            return False  # Stop listening

        if rc != paho.mqtt.client.MQTT_ERR_SUCCESS:
            # If known/expected error
            if rc == paho.mqtt.client.MQTT_ERR_CONN_LOST:
                log.warning("Connection lost, retrying")
            elif rc == paho.mqtt.client.MQTT_ERR_NOMEM:
                # This error is wrongly classified
                # See https://github.com/eclipse/paho.mqtt.python/issues/340
                log.warning("Connection error, retrying")
            else:
                err = paho.mqtt.client.error_string(rc)
                log.error("MQTT Error: %s", err)

            # Wait before reconnecting
            self._mqtt._reconnect_wait()

            # Try reconnecting
            self._configure_connect_options()
            try:
                self._mqtt.reconnect()
            except (
                # Taken from .loop_forever
                paho.mqtt.client.socket.error,
                OSError,
                paho.mqtt.client.WebsocketConnectionError,
            ) as e:
                log.debug("MQTT reconnection failed: %s", e)

        return True  # Keep listening

    def listen(self) -> Iterable[_events.Event]:
        """Run the listening loop continually.

        Yields events when they arrive.

        This will automatically reconnect on errors.

        Example:
            Print events continually.

            >>> for event in listener.listen():
            ...     print(event)
        """
        while self._loop_once():
            if self._tmp_events:
                yield from self._tmp_events
            self._tmp_events = None

    def disconnect(self) -> None:
        """Disconnect the MQTT listener.

        Can be called while listening, which will stop the listening loop.

        The `Listener` object should not be used after this is called!

        Example:
            Stop the listener when recieving a message with the text "/stop"

            >>> for event in listener.listen():
            ...     if isinstance(event, fbchat.MessageEvent):
            ...         if event.message.text == "/stop":
            ...             listener.disconnect()  # Almost the same "break"
        """
        self._mqtt.disconnect()

    def set_foreground(self, value: bool) -> None:
        """Set the `foreground` value while listening."""
        # TODO: Document what this actually does!
        payload = _util.json_minimal({"foreground": value})
        info = self._mqtt.publish("/foreground_state", payload=payload, qos=1)
        self._foreground = value
        # TODO: We can't wait for this, since the loop is running within the same thread
        # info.wait_for_publish()

    def set_chat_on(self, value: bool) -> None:
        """Set the `chat_on` value while listening."""
        # TODO: Document what this actually does!
        # TODO: Is this the right request to make?
        data = {"make_user_available_when_in_foreground": value}
        payload = _util.json_minimal(data)
        info = self._mqtt.publish("/set_client_settings", payload=payload, qos=1)
        self._chat_on = value
        # TODO: We can't wait for this, since the loop is running within the same thread
        # info.wait_for_publish()

    # def send_additional_contacts(self, additional_contacts):
    #     payload = _util.json_minimal({"additional_contacts": additional_contacts})
    #     info = self._mqtt.publish("/send_additional_contacts", payload=payload, qos=1)
    #
    # def browser_close(self):
    #     info = self._mqtt.publish("/browser_close", payload=b"{}", qos=1)
