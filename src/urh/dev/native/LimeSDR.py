import os
import time

import numpy as np

from urh.dev.native.Device import Device
from urh.dev.native.lib import limesdr


class LimeSDR(Device):
    READ_SAMPLES = 32768
    SEND_SAMPLES = 32768

    RECV_FIFO_SIZE = 4000000000
    SEND_FIFO_SIZE = 5 * SEND_SAMPLES

    LIME_TIMEOUT_RECEIVE_MS = 10
    LIME_TIMEOUT_SEND_MS = 500

    BYTES_PER_SAMPLE = 8  # We use dataFmt_t.LMS_FMT_F32 so we have 32 bit floats for I and Q
    DEVICE_LIB = limesdr
    DEVICE_METHODS = Device.DEVICE_METHODS.copy()
    DEVICE_METHODS.update({
        Device.Command.SET_FREQUENCY.name: "set_center_frequency",
        Device.Command.SET_BANDWIDTH.name: "set_lpf_bandwidth",
        Device.Command.SET_RF_GAIN.name: "set_normalized_gain"
    })

    @staticmethod
    def initialize_limesdr(freq, sample_rate, bandwidth, gain, ctrl_conn, is_tx):
        ret = limesdr.open()
        ctrl_conn.send("OPEN:" + str(ret))

        if ret != 0:
            return False

        ret = limesdr.init()
        ctrl_conn.send("INIT:" + str(ret))

        if ret != 0:
            return False

        # TODO Channel 0 currently hardcoded
        channel = 0
        limesdr.set_channel(channel)
        limesdr.set_tx(is_tx)
        limesdr.enable_channel(True, is_tx, channel)
        #if is_tx:
        #    lime_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lime_send.ini")
        #else:
        #    lime_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lime.ini")
        lime_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lime.ini")
        limesdr.load_config(lime_file)

        LimeSDR.process_command((LimeSDR.Command.SET_FREQUENCY.name, freq), ctrl_conn, is_tx)
        LimeSDR.process_command((LimeSDR.Command.SET_SAMPLE_RATE.name, sample_rate), ctrl_conn, is_tx)
        LimeSDR.process_command((LimeSDR.Command.SET_BANDWIDTH.name, bandwidth), ctrl_conn, is_tx)
        LimeSDR.process_command((LimeSDR.Command.SET_RF_GAIN.name, gain * 0.01), ctrl_conn, is_tx)

        antennas = limesdr.get_antenna_list()
        ctrl_conn.send("Current antenna is {0}".format(antennas[limesdr.get_antenna()]))
        ctrl_conn.send("Current chip temperature is {0:.2f}°C".format(limesdr.get_chip_temperature()))

        return True

    @staticmethod
    def shutdown_lime_sdr(ctrl_conn):
        limesdr.enable_channel(False, False, 0)
        limesdr.enable_channel(False, False, 1)
        limesdr.enable_channel(False, True, 0)
        limesdr.enable_channel(False, True, 1)
        ret = limesdr.close()
        ctrl_conn.send("CLOSE:" + str(ret))
        return True

    @staticmethod
    def lime_receive(data_conn, ctrl_conn, frequency: float, sample_rate: float, bandwidth: float, gain: float):
        if not LimeSDR.initialize_limesdr(frequency, sample_rate, bandwidth, gain, ctrl_conn, is_tx=False):
            return False

        exit_requested = False

        limesdr.setup_stream(LimeSDR.RECV_FIFO_SIZE)
        limesdr.start_stream()

        while not exit_requested:
            limesdr.recv_stream(data_conn, LimeSDR.READ_SAMPLES, LimeSDR.LIME_TIMEOUT_RECEIVE_MS)
            while ctrl_conn.poll():
                result = LimeSDR.process_command(ctrl_conn.recv(), ctrl_conn, is_tx=False)
                if result == LimeSDR.Command.STOP.name:
                    exit_requested = True
                    break

        limesdr.stop_stream()
        limesdr.destroy_stream()
        LimeSDR.shutdown_lime_sdr(ctrl_conn)
        data_conn.close()
        ctrl_conn.close()

    @staticmethod
    def lime_send(ctrl_connection, frequency: float, sample_rate: float, bandwidth: float, gain: float,
                  samples_to_send, current_sent_index, current_sending_repeat, sending_repeats):
        def sending_is_finished():
            if sending_repeats == 0:  # 0 = infinity
                return False

            return current_sending_repeat.value >= sending_repeats and current_sent_index.value >= len(samples_to_send)

        if not LimeSDR.initialize_limesdr(frequency, sample_rate, bandwidth, gain, ctrl_connection, is_tx=True):
            return False

        exit_requested = False
        num_samples = LimeSDR.SEND_SAMPLES

        limesdr.setup_stream(LimeSDR.SEND_FIFO_SIZE)
        limesdr.start_stream()

        while not exit_requested and not sending_is_finished():
            limesdr.send_stream(samples_to_send[current_sent_index.value:current_sent_index.value+num_samples], LimeSDR.LIME_TIMEOUT_SEND_MS)
            current_sent_index.value += num_samples
            if current_sent_index.value >= len(samples_to_send) - 1:
                current_sending_repeat.value += 1
                if current_sending_repeat.value < sending_repeats or sending_repeats == 0:  # 0 = infinity
                    current_sent_index.value = 0
                else:
                    current_sent_index.value = len(samples_to_send)

            while ctrl_connection.poll():
                result = LimeSDR.process_command(ctrl_connection.recv(), ctrl_connection, is_tx=True)
                if result == LimeSDR.Command.STOP.name:
                    exit_requested = True
                    break

        limesdr.stop_stream()
        limesdr.destroy_stream()
        LimeSDR.shutdown_lime_sdr(ctrl_connection)
        ctrl_connection.close()

    def __init__(self, center_freq, sample_rate, bandwidth, gain, if_gain=1, baseband_gain=1, is_ringbuffer=False):
        super().__init__(center_freq=center_freq, sample_rate=sample_rate, bandwidth=bandwidth,
                         gain=gain, if_gain=if_gain, baseband_gain=baseband_gain, is_ringbuffer=is_ringbuffer)
        self.success = 0

        self.receive_process_function = LimeSDR.lime_receive
        self.send_process_function = LimeSDR.lime_send

    def set_device_gain(self, gain):
        try:
            self.parent_ctrl_conn.send((self.Command.SET_RF_GAIN.name, gain * 0.01))
        except BrokenPipeError:
            pass

    @property
    def current_sent_sample(self):
        # We can pass samples directly to LimeSDR API and do not need to convert to bytes,
        # however we need to pass float values so we need to divide by 2
        return self._current_sent_sample.value // 2

    @current_sent_sample.setter
    def current_sent_sample(self, value: int):
        # We can pass samples directly to LimeSDR API and do not need to convert to bytes
        self._current_sent_sample.value = value * 2

    @property
    def receive_process_arguments(self):
        return self.child_data_conn, self.child_ctrl_conn, self.frequency, self.sample_rate, self.bandwidth, self.gain

    @property
    def send_process_arguments(self):
        return self.child_ctrl_conn, self.frequency, self.sample_rate, self.bandwidth, self.gain, \
               self.samples_to_send.view(np.float32), self._current_sent_sample, self._current_sending_repeat, self.sending_repeats

    @staticmethod
    def unpack_complex(buffer, nvalues: int):
        result = np.empty(nvalues, dtype=np.complex64)
        unpacked = np.frombuffer(buffer, dtype=[('r', np.float32), ('i', np.float32)])
        result.real = unpacked["r"]
        result.imag = unpacked["i"]
        return result

    @staticmethod
    def pack_complex(complex_samples: np.ndarray):
        assert complex_samples.dtype == np.complex64
        # tostring() is a compatibility (numpy<1.9) alias for tobytes(). Despite its name it returns bytes not strings.
        return complex_samples.view(np.float32).tostring()