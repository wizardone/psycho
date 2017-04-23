'''
Created on 29 juli 2016

'''

import atexit
import threading

from tobiiresearch.interop import tobii_pro_internal
from tobiiresearch.implementation.DisplayArea import DisplayArea
from tobiiresearch.implementation.TrackBox import TrackBox
from tobiiresearch.implementation.Errors import EyeTrackerOperationFailedError
from tobiiresearch.implementation.Errors import _on_error_raise_exception
from tobiiresearch.implementation.License import FailedLicense

_tobii_pro_calibration_failure = 0
_tobii_pro_calibration_success = 1

tobii_pro_internal.startup()
atexit.register(tobii_pro_internal.cleanup)


class TobiiProEyeTrackerData(object):
    def __init__(self, dictionary):
        self.address = dictionary["address"]
        self.device_name = dictionary["device_name"]
        self.serial_number = dictionary["serial_number"]
        self.model = dictionary["model"]
        self.firmware_version = dictionary["firmware_version"]
        self.device_capabilities = dictionary["device_capabilities"]


class TobiiProCalibrationPoint(object):
    def __init__(self, dictionary):
        self.position = dictionary["position"]
        self.left_sample_position = dictionary["left_sample_position"]
        self.left_validity = dictionary["left_validity"]
        self.right_sample_position = dictionary["right_sample_position"]
        self.right_validity = dictionary["right_validity"]


class TobiiProCallback(object):
    def __init__(self, address, stream_name, user_callback):
        self.__address = address
        self.__stream_name = stream_name
        self.__user_callback = user_callback

    def __call__(self, dictionary_with_data):
        try:
            self.__user_callback(dictionary_with_data)
        except Exception as e:
            if len(self.__stream_name) > 0:
                tobii_pro_internal.\
                    report_stream_error(self.__address,
                                        "User {0} callback raised exception {1}. Message: {2}".
                                        format(self.__stream_name, type(e).__name__, str(e)))


__callbacks = {}
__callback_lock = threading.RLock()
__subscribe_lock = threading.RLock()


def __subscription_callback(subscription_type, address, data):
    global __callbacks
    global __callback_lock
    callbacks = []
    with __callback_lock:
        for callback in __callbacks.get((subscription_type, address), {}).itervalues():
            callbacks.append(callback)
    for callback in callbacks:
        callback(data)


def find_all_eyetrackers():
    result = tobii_pro_internal.find_all_eyetrackers()
    _on_error_raise_exception(result[0])
    return [TobiiProEyeTrackerData(x) for x in result[1]]


def get_device(address):
    result = tobii_pro_internal.get_device(address)
    _on_error_raise_exception(result[0])
    return TobiiProEyeTrackerData(result[1])


def subscribe_to(subscription_type, stream_name, tracker, callback):
    global __callbacks
    global __callback_lock
    global __subscribe_lock
    with __subscribe_lock:
        address = "" if tracker is None else tracker.address
        subscription_tuple = (subscription_type, address)
        with __callback_lock:
            __callbacks.setdefault(subscription_tuple, {})[tracker] =\
                TobiiProCallback(address, stream_name, callback)
            count = len(__callbacks[subscription_tuple])
        if count == 1:
            status = tobii_pro_internal.subscribe_to(subscription_type, address,
                                                     lambda x: __subscription_callback(subscription_type, address, x))
            _on_error_raise_exception(status[0])


def unsubscribe_from(subscription_type, tracker):
    global __callbacks
    global __callback_lock
    global __subscribe_lock
    with __subscribe_lock:
        address = "" if tracker is None else tracker.address
        subscription_tuple = (subscription_type, address)
        unsubscribe = False
        with __callback_lock:
            if subscription_tuple in __callbacks:
                if tracker in __callbacks[subscription_tuple]:
                    del __callbacks[subscription_tuple][tracker]
                if len(__callbacks[subscription_tuple]) == 0:
                    del __callbacks[subscription_tuple]
                    unsubscribe = True
        if unsubscribe:
            status = tobii_pro_internal.unsubscribe_from(subscription_type, address)
            _on_error_raise_exception(status[0])


def apply_licenses(address, licenses):
    result = tobii_pro_internal.apply_licenses(address, licenses)
    _on_error_raise_exception(result[0])
    return tuple([FailedLicense(key, validation) for key, validation in zip(licenses, result[1]) if validation != 0])


def clear_applied_licenses(address):
    status = tobii_pro_internal.clear_applied_licenses(address)
    _on_error_raise_exception(status[0])


def get_all_gaze_output_frequencies(address):
    result = tobii_pro_internal.get_all_gaze_output_frequencies(address)
    _on_error_raise_exception(result[0])
    return tuple(result[1])


def get_gaze_output_frequency(address):
    result = tobii_pro_internal.get_gaze_output_frequency(address)
    _on_error_raise_exception(result[0])
    return result[1]


def set_gaze_output_frequency(address, frame_rate):
    status = tobii_pro_internal.set_gaze_output_frequency(address, frame_rate)
    _on_error_raise_exception(status[0])


def get_all_eye_tracking_modes(address):
    result = tobii_pro_internal.get_all_eye_tracking_modes(address)
    _on_error_raise_exception(result[0])
    return tuple(result[1])


def get_eye_tracking_mode(address):
    result = tobii_pro_internal.get_eye_tracking_mode(address)
    _on_error_raise_exception(result[0])
    return result[1]


def set_eye_tracking_mode(address, eye_tracking_mode):
    status = tobii_pro_internal.set_eye_tracking_mode(address, eye_tracking_mode)
    _on_error_raise_exception(status[0])


def screen_based_calibration_enter_calibration_mode(address):
    status = tobii_pro_internal.screen_based_calibration_enter_calibration_mode(address)
    _on_error_raise_exception(status[0])


def screen_based_calibration_leave_calibration_mode(address):
    status = tobii_pro_internal.screen_based_calibration_leave_calibration_mode(address)
    _on_error_raise_exception(status[0])


def screen_based_calibration_collect_data(address, x, y):
    status = tobii_pro_internal.screen_based_calibration_collect_data(address, x, y)
    try:
        _on_error_raise_exception(status[0])
        return _tobii_pro_calibration_success
    except EyeTrackerOperationFailedError:
        pass
    return _tobii_pro_calibration_failure


def screen_based_calibration_discard_data(address, x, y):
    status = tobii_pro_internal.screen_based_calibration_discard_data(address, x, y)
    _on_error_raise_exception(status[0])


def screen_based_calibration_compute_and_apply(address):
    status = tobii_pro_internal.screen_based_calibration_compute_and_apply(address)
    try:
        _on_error_raise_exception(status[0])
        result = tobii_pro_internal.screen_based_calibration_get_calibration_points(address)
        _on_error_raise_exception(result[0])
        return (_tobii_pro_calibration_success, [TobiiProCalibrationPoint(x) for x in result[1]])
    except EyeTrackerOperationFailedError:
        pass
    return (_tobii_pro_calibration_failure,)


def calibration_retrieve(address):
    result = tobii_pro_internal.calibration_retrieve(address)
    _on_error_raise_exception(result[0])
    if result[1] is None:
        return None
    else:
        return bytes(result[1])


def calibration_apply(address, data):
    if not isinstance(data, bytes):
        raise ValueError("Calibration data must be applied with a bytes object.")
    status = tobii_pro_internal.calibration_apply(address, bytearray(data))
    _on_error_raise_exception(status[0])


def get_display_area(address):
    result = tobii_pro_internal.get_display_area(address)
    _on_error_raise_exception(result[0])
    return DisplayArea(result[1])


def get_track_box(address):
    result = tobii_pro_internal.get_track_box(address)
    _on_error_raise_exception(result[0])
    return TrackBox(result[1])


def get_system_time_stamp():
    result = tobii_pro_internal.get_system_time_stamp()
    _on_error_raise_exception(result[0])
    return result[1]


def get_sdk_version():
    result = tobii_pro_internal.get_sdk_version()
    _on_error_raise_exception(result[0])
    return result[1]


def set_device_name(address, device_name):
    status = tobii_pro_internal.set_device_name(address, device_name)
    _on_error_raise_exception(status[0])
