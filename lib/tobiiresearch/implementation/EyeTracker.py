from tobiiresearch.interop import tobii_pro
from tobiiresearch.implementation.Errors import _on_error_raise_exception
from tobiiresearch.implementation.EyeImageData import EyeImageData
from tobiiresearch.implementation.ExternalSignalData import ExternalSignalData
from tobiiresearch.implementation.GazeData import GazeData
from tobiiresearch.implementation._LogEntry import _LogEntry
from tobiiresearch.implementation.Notifications import CalibrationModeEnteredData, CalibrationModeLeftData
from tobiiresearch.implementation.Notifications import ConnectionLostData, ConnectionRestoredData
from tobiiresearch.implementation.Notifications import DisplayAreaChangedData, GazeOutputFrequencyChangedData
from tobiiresearch.implementation.Notifications import TrackBoxChangedData
from tobiiresearch.implementation.StreamErrorData import StreamErrorData
from tobiiresearch.implementation.TimeSynchronizationData import TimeSynchronizationData
import threading

_EYETRACKER_NOTIFICATIONS = "_eyetracker_notifications"

_invalid_parameter = 10  # __TobiiProStatus.invalid_parameter
_invalid_operation = 11  # __TobiiProStatus.invalid_operation


##
# Indicates that the device can have display areas set.
#
# Value in tuple EyeTracker.device_capabilities
# <CodeExample>create_eyetracker.py</CodeExample>
CAPABILITY_CAN_SET_DISPLAY_AREA = "capability_can_set_display_area"

##
# Indicates that the device can deliver an external signal stream.
#
# Value in tuple EyeTracker.device_capabilities
# <CodeExample>create_eyetracker.py</CodeExample>
CAPABILITY_HAS_EXTERNAL_SIGNAL = "capability_has_external_signal"

##
# Indicates that the device can deliver an eye image stream.
#
# Value in tuple EyeTracker.device_capabilities
# <CodeExample>create_eyetracker.py</CodeExample>
CAPABILITY_HAS_EYE_IMAGES = "capability_has_eye_images"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for external signal.
#
# You will get a callback when the value of the external signal port (TTL input) on the eye tracker device changes. Not
# all eye trackers have an output trigger port. The output feature could be used to synchronize the eye tracker data
# with data from other devices. The output data contains a time reference that matches the time reference on the time
# synchronized gaze data. Callbacks will receive an ExternalSignalData object or a dictionary with values if
# as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>external_signal.py</CodeExample>
EYETRACKER_EXTERNAL_SIGNAL = "eyetracker_external_signal"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for eye images.
#
# You will get a callback when a new eye image is received, and the occurrence depends on the eye tracker model. Not all
# eye tracker models support this feature. If no one is listening to gaze data, the eye tracker will only deliver full
# images, otherwise either cropped or full images will be delivered depending on whether or not the eye tracker has
# detected eyes. Callbacks will receive an EyeImageData object or a dictionary with values if as_dictionary is True.
EYETRACKER_EYE_IMAGES = "eyetracker_eye_images"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for gaze data.
#
# You will get a callback when time synchronized gaze is received. Time synchronized gaze is not supported on all eye
# trackers, other eye trackers need additional license to activate this support. Callbacks will receive a GazeData
# object or a dictionary with values if as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>gaze_data.py</CodeExample>
EYETRACKER_GAZE_DATA = "eyetracker_gaze_data"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for calibration mode entered messages.
#
# You will get a callback when calibration mode is entered. Callbacks will receive a CalibrationModeEnteredData object
# or a dictionary with values if as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>notifications.py</CodeExample>
EYETRACKER_NOTIFICATION_CALIBRATION_MODE_ENTERED = "eyetracker_notification_calibration_mode_entered"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for calibration mode left messages.
#
# You will get a callback when calibration mode is left. Callbacks will receive a CalibrationModeLeftData object
# or a dictionary with values if as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>notifications.py</CodeExample>
EYETRACKER_NOTIFICATION_CALIBRATION_MODE_LEFT = "eyetracker_notification_calibration_mode_left"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for connection lost messages.
#
# You will get a callback when connection to the eye tracker is lost. Callbacks will receive a ConnectionLostData
# object or a dictionary with values if as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>notifications.py</CodeExample>
EYETRACKER_NOTIFICATION_CONNECTION_LOST = "eyetracker_notification_connection_lost"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for connection restored messages.
#
# You will get a callback when connection to the eye tracker is restored. Callbacks will receive a
# ConnectionRestoredData object or a dictionary with values if as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>notifications.py</CodeExample>
EYETRACKER_NOTIFICATION_CONNECTION_RESTORED = "eyetracker_notification_connection_restored"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for display area changed messages.
#
# You will get a callback when the display area is changed. Callbacks will receive a DisplayAreaChangedData object
# or a dictionary with values if as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>notifications.py</CodeExample>
EYETRACKER_NOTIFICATION_DISPLAY_AREA_CHANGED = "eyetracker_notification_display_area_changed"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for gaze output frequency changed messages.
#
# You will get a callback when the gaze output frequency is changed. Callbacks will receive a
# GazeOutputFrequencyChangedData object or a dictionary with values if as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>notifications.py</CodeExample>
EYETRACKER_NOTIFICATION_GAZE_OUTPUT_FREQUENCY_CHANGED = "eyetracker_notification_gaze_output_frequency_changed"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for track box changed messages.
#
# You will get a callback when the track box is changed. Callbacks will receive a TrackBoxChangedData object or a
# dictionary with values if as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>notifications.py</CodeExample>
EYETRACKER_NOTIFICATION_TRACK_BOX_CHANGED = "eyetracker_notification_track_box_changed"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for stream errors.
#
# You will get a callback when an error occurs on other streams. You can get errors when subscribing, when something
# happened to the connection in the stream pump or when an error was raised in a callback. Callbacks will receive a
# StreamErrorData object or a dictionary with values if as_dictionary is True.
EYETRACKER_STREAM_ERRORS = "eyetracker_stream_errors"

##
# Used in EyeTracker.subscribe_to and EyeTracker.unsubscribe_from for time synchronization data.
#
# You will get a callback when the computer and the eye trackers clocks gets synchronized. To handle normal drifts
# between clocks the clocks are checked on regular basis, and this results in that the time stamps are adjusted for the
# drifts in the data streams. This drift handling is done in real time. The data received from this event could be used
# for an even more accurate drift adjustment in the post processing. Callbacks will receive a TimeSynchronizationData
# object or a dictionary with values if as_dictionary is True.
# See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
# <CodeExample>time_synchronization_data.py</CodeExample>
EYETRACKER_TIME_SYNCHRONIZATION_DATA = "eyetracker_time_synchronization_data"

_available_notification_subscriptions =\
    {EYETRACKER_NOTIFICATION_CONNECTION_LOST: ConnectionLostData,
     EYETRACKER_NOTIFICATION_CONNECTION_RESTORED: ConnectionRestoredData,
     EYETRACKER_NOTIFICATION_CALIBRATION_MODE_ENTERED: CalibrationModeEnteredData,
     EYETRACKER_NOTIFICATION_CALIBRATION_MODE_LEFT: CalibrationModeLeftData,
     EYETRACKER_NOTIFICATION_TRACK_BOX_CHANGED: TrackBoxChangedData,
     EYETRACKER_NOTIFICATION_DISPLAY_AREA_CHANGED: DisplayAreaChangedData,
     EYETRACKER_NOTIFICATION_GAZE_OUTPUT_FREQUENCY_CHANGED: GazeOutputFrequencyChangedData}

# The order of these numbers have to be the same as in the enum CallbackType in py_callbacks.h
_subscription_types = {EYETRACKER_GAZE_DATA:
                       {"type_index": 1,
                        "stream_name": "gaze data",
                        "data_class": GazeData},
                       EYETRACKER_EXTERNAL_SIGNAL:
                       {"type_index": 2,
                        "stream_name": "external signal",
                        "data_class": ExternalSignalData},
                       EYETRACKER_TIME_SYNCHRONIZATION_DATA:
                       {"type_index": 3,
                        "stream_name": "time synchronization data",
                        "data_class": TimeSynchronizationData},
                       EYETRACKER_STREAM_ERRORS:
                       {"type_index": 4,
                        "stream_name": "",
                        "data_class": StreamErrorData},
                       _EYETRACKER_NOTIFICATIONS:
                       {"type_index": 5,
                        "stream_name":
                        "notifications",
                        "data_class": dict},
                       EYETRACKER_EYE_IMAGES:
                       {"type_index": 6,
                        "stream_name": "eye images",
                        "data_class": EyeImageData},
                       }


def __log_callback(user_callback, as_dictionary, data_dict):
    if as_dictionary:
        user_callback(data_dict)
    else:
        user_callback(_LogEntry(data_dict))


def _logging_subscribe(callback, as_dictionary=False):
    tobii_pro.subscribe_to(0, "", None, lambda x: __log_callback(callback, as_dictionary, x))


def _logging_unsubscribe():
    tobii_pro.unsubscribe_from(0, None)


class EyeTracker(object):
    '''Provides methods and properties to manage and get data from an eye tracker.

    EyeTracker objects are either created from an address or returned in a tuple from @ref find_all_eyetrackers.
    '''

    def __init__(self, address):
        '''Gets an eye tracker object that has the specified URI.

        <CodeExample>create_eyetracker.py</CodeExample>
        Args:
        address: Address (URI) to the eye tracker.

        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        ValueError
        '''

        if type(address) is str:
            self.__init_from_uri(address)
        elif isinstance(address, tobii_pro.TobiiProEyeTrackerData):
            self.__init_from_data(address)
        else:
            raise ValueError("An EyeTracker must be initialized with a URI.")

        self.__notification_subscription_lock = threading.RLock()
        self.__notification_subscriptions = {}
        self.__subscription_lock = threading.RLock()
        self.__subscriptions = {}

    def __del__(self):
        with self.__subscription_lock:
            for subscription_type in self.__subscriptions.iterkeys():
                tobii_pro.unsubscribe_from(subscription_type, self)

    def __init_from_uri(self, address):
        self.__init_from_data(tobii_pro.get_device(address))

    def __init_from_data(self, data):
        self.__address = data.address
        self.__device_name = data.device_name
        self.__serial_number = data.serial_number
        self.__model = data.model
        self.__firmware_version = data.firmware_version
        self.__device_capabilities = data.device_capabilities

    def __notification_callback(self, data):
        with self.__notification_subscription_lock:
            for callback, as_dictionary in\
                    self.__notification_subscriptions.get(data["notification_type"], {}).iteritems():
                data_class = dict if as_dictionary else _available_notification_subscriptions[data["notification_type"]]
                callback(data_class(data))

    def __subscription_callback(self, subscription_type, data):
        global _subscription_types
        with self.__subscription_lock:
            for callback, as_dictionary in self.__subscriptions.get(subscription_type, {}).iteritems():
                data_class = dict if as_dictionary else _subscription_types[subscription_type]["data_class"]
                callback(data_class(data))

    @property
    def address(self):
        '''Gets the address (URI) of the eye tracker device.
        '''
        return self.__address

    @property
    def device_name(self):
        '''Gets the name of the eye tracker.
        '''
        return self.__device_name

    @property
    def serial_number(self):
        '''Gets the serial number of the eye tracker. All physical eye trackers have a unique serial number.
        '''
        return self.__serial_number

    @property
    def model(self):
        '''Gets the model of the eye tracker.
        '''
        return self.__model

    @property
    def firmware_version(self):
        '''Gets the firmware version of the eye tracker.
        '''
        return self.__firmware_version

    @property
    def device_capabilities(self):
        '''Gets a tuple with the capabilities of the device.

        Valid values in the tuple are @ref CAPABILITY_CAN_SET_DISPLAY_AREA, @ref CAPABILITY_HAS_EXTERNAL_SIGNAL and
        @ref CAPABILITY_HAS_EYE_IMAGES.
        '''
        return self.__device_capabilities

    def apply_licenses(self, license_key_ring):
        '''Sets a key ring of licenses or a single license for unlocking features of the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>apply_licenses.py</CodeExample>
        Args:
        license_key_ring: List of LicenseKey objects, list of bytes, LicenseKey object or bytes object.

        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        AttributeError
        TypeError

        Returns:
        Tuple of FailedLicense objects for licenses that failed.
        Empty tuple if all licenses were successfully applied.
        '''
        if isinstance(license_key_ring, bytes):
            return tobii_pro.apply_licenses(self.__address, (license_key_ring,))
        elif hasattr(license_key_ring, 'key_string'):
            return tobii_pro.apply_licenses(self.__address, (license_key_ring.key_string,))
        else:
            return tobii_pro.apply_licenses(self.__address, tuple([(lambda key: key
                                                                    if isinstance(key, bytes) else key.key_string)(key)
                                                                   for key in license_key_ring]))

    def clear_applied_licenses(self):
        '''Clears any previously applied licenses.

        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError
        '''
        return tobii_pro.clear_applied_licenses(self.__address)

    def retrieve_calibration_data(self):
        '''Gets the calibration data used currently by the eye tracker.

        This data can be saved to a file for later use.
        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>calibration_data.py</CodeExample>

        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError
        '''
        return tobii_pro.calibration_retrieve(self.__address)

    def apply_calibration_data(self, calibration_data):
        '''Sets the provided calibration data to the eye tracker, which means it will be active calibration.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>calibration_data.py</CodeExample>
        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError
        ValueError
        '''
        tobii_pro.calibration_apply(self.__address, calibration_data)

    def get_all_gaze_output_frequencies(self):
        '''Gets a list of gaze output frequencies supported by the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>gaze_output_frequencies.py</CodeExample>
        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError

        Returns:
        Tuple of floats with all gaze output frequencies.
        '''
        return tobii_pro.get_all_gaze_output_frequencies(self.__address)

    def get_gaze_output_frequency(self):
        '''Gets the gaze output frequency of the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>gaze_output_frequencies.py</CodeExample>
        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError

        Returns:
        Float with the current gaze output frequency.
        '''
        return tobii_pro.get_gaze_output_frequency(self.__address)

    def set_gaze_output_frequency(self, gaze_output_frequency):
        '''Sets the gaze output frequency of the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>gaze_output_frequencies.py</CodeExample>
        Args:
        gaze_output_frequency: The gaze output frequency as a float value.

        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError
        ValueError
        '''
        return tobii_pro.set_gaze_output_frequency(self.__address, gaze_output_frequency)

    def get_all_eye_tracking_modes(self):
        '''Gets a tuple of eye tracking modes supported by the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>eye_tracking_modes.py</CodeExample>
        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError

        Returns:
        Tuple of strings with available eye tracking modes.
        '''
        return tobii_pro.get_all_eye_tracking_modes(self.__address)

    def get_eye_tracking_mode(self):
        '''Gets the eye tracking mode of the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>eye_tracking_modes.py</CodeExample>
        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError

        Returns:
        String with the current eye tracking mode.
        '''
        return tobii_pro.get_eye_tracking_mode(self.__address)

    def set_eye_tracking_mode(self, eye_tracking_mode):
        '''Sets the eye tracking mode of the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>eye_tracking_modes.py</CodeExample>
        Args:
        eye_tracking_mode: The eye tracking mode as a string.

        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError
        ValueError
        '''
        return tobii_pro.set_eye_tracking_mode(self.__address, eye_tracking_mode)

    def get_track_box(self):
        '''Gets the track box of the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>get_track_box.py</CodeExample>
        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError

        Returns:
        Track box in the user coordinate system as a TrackBox object.
        '''
        return tobii_pro.get_track_box(self.__address)

    def get_display_area(self):
        ''' Gets the size and corners of the display area.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>get_display_area.py</CodeExample>
        Raises:
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError

        Returns:
        Display area in the user coordinate system as a DisplayArea object.
        '''
        return tobii_pro.get_display_area(self.__address)

    def set_device_name(self, device_name):
        '''Changes the device name. This is not supported by all eye trackers.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        <CodeExample>set_device_name.py</CodeExample>
        Args:
        device_name: The eye tracker's desired name.

        Raises:
        EyeTrackerFeatureNotSupportedError
        EyeTrackerConnectionFailedError
        EyeTrackerInternalError
        EyeTrackerLicenseError
        '''
        tobii_pro.set_device_name(self.__address, device_name)
        self.__init_from_data(tobii_pro.get_device(self.__address))

    def subscribe_to(self, subscription_type, callback, as_dictionary=False):
        '''Subscribes to data for the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        You can subscribe to @ref EYETRACKER_EXTERNAL_SIGNAL, @ref EYETRACKER_GAZE_DATA,
        @ref EYETRACKER_NOTIFICATION_CONNECTION_LOST, @ref EYETRACKER_NOTIFICATION_CONNECTION_RESTORED,
        @ref EYETRACKER_NOTIFICATION_CALIBRATION_MODE_ENTERED, @ref EYETRACKER_NOTIFICATION_CALIBRATION_MODE_LEFT,
        @ref EYETRACKER_NOTIFICATION_TRACK_BOX_CHANGED, @ref EYETRACKER_NOTIFICATION_DISPLAY_AREA_CHANGED,
        @ref EYETRACKER_NOTIFICATION_GAZE_OUTPUT_FREQUENCY_CHANGED,
        @ref EYETRACKER_TIME_SYNCHRONIZATION_DATA or @ref EYETRACKER_STREAM_ERRORS.
        <CodeExample>gaze_data.py</CodeExample>
        Args:
        subscription_type: Type of data to subscribe to.
        callback: Callback receiveing the data. See documentation of subscription types for details.
        as_dictionary: If True, the callback will receive a dictionary with values instead of a custom object.
        '''
        global _available_notification_subscriptions
        global _EYETRACKER_NOTIFICATIONS_BASE
        global _subscription_types

        if not callable(callback):
            _on_error_raise_exception(_invalid_parameter)

        # Special handling of notification subscribtions.
        if subscription_type in _available_notification_subscriptions.keys():
            with self.__notification_subscription_lock:
                # Subscribing more than once for the same type with the same callback is invalid.
                if ((subscription_type in self.__notification_subscriptions and
                     callback in self.__notification_subscriptions[subscription_type])):
                    _on_error_raise_exception(_invalid_operation)
                count = len(self.__notification_subscriptions)
                self.__notification_subscriptions.setdefault(subscription_type, {})[callback] = as_dictionary
                if count == 0:
                    self.subscribe_to(_EYETRACKER_NOTIFICATIONS, self.__notification_callback)
        else:
            if subscription_type not in _subscription_types:
                _on_error_raise_exception(_invalid_parameter)
            with self.__subscription_lock:
                # Subscribing more than once for the same type with the same callback is invalid.
                if subscription_type in self.__subscriptions and callback in self.__subscriptions[subscription_type]:
                    _on_error_raise_exception(_invalid_operation)
                self.__subscriptions.setdefault(subscription_type, {})[callback] = as_dictionary
                if len(self.__subscriptions[subscription_type]) == 1:
                    tobii_pro.subscribe_to(_subscription_types[subscription_type]["type_index"],
                                           _subscription_types[subscription_type]["stream_name"],
                                           self, lambda x, st=subscription_type: self.__subscription_callback(st, x))

    def unsubscribe_from(self, subscription_type, callback=None):
        '''Unsubscribes from data for the eye tracker.

        See @ref find_all_eyetrackers or EyeTracker.__init__ on how to create an EyeTracker object.
        You can unsubscribe from @ref EYETRACKER_EXTERNAL_SIGNAL, @ref EYETRACKER_GAZE_DATA,
        @ref EYETRACKER_NOTIFICATION_CONNECTION_LOST, @ref EYETRACKER_NOTIFICATION_CONNECTION_RESTORED,
        @ref EYETRACKER_NOTIFICATION_CALIBRATION_MODE_ENTERED, @ref EYETRACKER_NOTIFICATION_CALIBRATION_MODE_LEFT,
        @ref EYETRACKER_NOTIFICATION_TRACK_BOX_CHANGED, @ref EYETRACKER_NOTIFICATION_DISPLAY_AREA_CHANGED,
        @ref EYETRACKER_NOTIFICATION_GAZE_OUTPUT_FREQUENCY_CHANGED,
        @ref EYETRACKER_TIME_SYNCHRONIZATION_DATA or @ref EYETRACKER_STREAM_ERRORS.
        <CodeExample>gaze_data.py</CodeExample>
        Args:
        subscription_type: Type of data to unsubscribe from.
        callback: Callback sent to subscribe_to or None to unsubscribe all subscriptions of this type.
        '''
        global _available_notification_subscriptions
        global _EYETRACKER_NOTIFICATIONS_BASE

        # Special handling of notification subscribtions.
        if subscription_type in _available_notification_subscriptions.keys():
            with self.__notification_subscription_lock:
                if subscription_type in self.__notification_subscriptions:
                    if callback in self.__notification_subscriptions[subscription_type]:
                        del self.__notification_subscriptions[subscription_type][callback]
                    if callback is None or len(self.__notification_subscriptions[subscription_type]) == 0:
                        del self.__notification_subscriptions[subscription_type]
                    if len(self.__notification_subscriptions) == 0:
                        self.unsubscribe_from(_EYETRACKER_NOTIFICATIONS, None)
        else:
            if subscription_type not in _subscription_types:
                _on_error_raise_exception(_invalid_parameter)
            with self.__subscription_lock:
                if subscription_type in self.__subscriptions:
                    if callback in self.__subscriptions[subscription_type]:
                        del self.__subscriptions[subscription_type][callback]
                    if callback is None or len(self.__subscriptions[subscription_type]) == 0:
                        del self.__subscriptions[subscription_type]
                        tobii_pro.unsubscribe_from(_subscription_types[subscription_type]["type_index"], self)


def find_all_eyetrackers():
    '''Finds eye trackers connected to the computer or the network.

    Please note that subsequent calls to find_all_eyetrackers() may return the eye trackers in a different order.

    <CodeExample>find_all_trackers.py</CodeExample>
    Raises:
    EyeTrackerInternalError

    Returns:
    A tuple of EyeTracker objects found.
    '''
    return tuple(EyeTracker(x) for x in tobii_pro.find_all_eyetrackers())


def get_system_time_stamp():
    '''Retrieves the time stamp from the system clock in microseconds.

    <CodeExample>get_system_time_stamp.py</CodeExample>
    Raises:
    EyeTrackerInternalError
    '''
    return tobii_pro.get_system_time_stamp()
