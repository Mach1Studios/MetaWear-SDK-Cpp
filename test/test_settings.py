from common import TestMetaWearBase
from ctypes import *
from mbientlab.metawear.cbindings import BatteryState, FnVoid_VoidP_Int, LedColor, LedPattern, Const

class TestSettings(TestMetaWearBase):
    def test_set_name(self):
        expected= [0x11, 0x01, 0x41, 0x6e, 0x74, 0x69, 0x57, 0x61, 0x72, 0x65]

        device_name= create_string_buffer(b'AntiWare', 8)
        bytes = cast(device_name, POINTER(c_ubyte))
        self.libmetawear.mbl_mw_settings_set_device_name(self.board, bytes, len(device_name.raw))

        self.assertEqual(self.command, expected)

    def test_set_tx_power(self):
        expected= [0x11, 0x03, 0xec]

        self.libmetawear.mbl_mw_settings_set_tx_power(self.board, -20)
        self.assertEqual(self.command, expected)

    def test_set_scan_response(self):
        expected_cmds= [
            [0x11, 0x08, 0x03, 0x03, 0xd8, 0xfe, 0x10, 0x16, 0xd8, 0xfe, 0x00, 0x12, 0x00, 0x6d, 0x62],
            [0x11, 0x07, 0x69, 0x65, 0x6e, 0x74, 0x6c, 0x61, 0x62, 0x00]
        ]

        scan_response= create_string_buffer(b'\x03\x03\xD8\xfe\x10\x16\xd8\xfe\x00\x12\x00\x6d\x62\x69\x65\x6e\x74\x6c\x61\x62\x00', 21)
        bytes = cast(scan_response, POINTER(c_ubyte))
        self.libmetawear.mbl_mw_settings_set_scan_response(self.board, bytes, len(scan_response.raw))
        self.assertEqual(self.command_history, expected_cmds)

    def test_start_advertising(self):
        expected= [0x11, 0x5]

        self.libmetawear.mbl_mw_settings_start_advertising(self.board)
        self.assertEqual(self.command, expected)

    def test_set_conn_params(self):
        expected= [0x11, 0x09, 0x58, 0x02, 0x20, 0x03, 0x80, 0x00, 0x66, 0x06]

        self.libmetawear.mbl_mw_settings_set_connection_parameters(self.board, 750.0, 1000.0, 128, 16384)
        self.assertEqual(self.command, expected)

    def test_set_ad_interval(self):
        expected= [0x11, 0x02, 0xa1, 0x01, 0x0]
        self.libmetawear.mbl_mw_settings_set_ad_interval(self.board, 417, 0)
        self.assertEqual(self.command, expected)

class TestSettingsRevision1(TestMetaWearBase):
    def setUp(self):
        self.metawear_r_services[0x11]= create_string_buffer(b'\x11\x80\x00\x01', 4)
        super().setUp()

    def test_set_ad_interval(self):
        self.libmetawear.mbl_mw_metawearboard_initialize(self.board, self.initialized_fn)

        expected= [0x11, 0x02, 0x9b, 0x02, 0xb4]
        self.libmetawear.mbl_mw_settings_set_ad_interval(self.board, 417, 180)
        self.assertEqual(self.command, expected)

    def test_disconnected_event_null(self):
        event= self.libmetawear.mbl_mw_settings_get_disconnect_event(self.board)
        self.assertEqual(event, None)

    def test_battery_state_data_null(self):
        signal= self.libmetawear.mbl_mw_settings_get_battery_state_data_signal(self.board)
        self.assertEqual(signal, None)

class TestSettingsRevision2(TestMetaWearBase):
    def setUp(self):
        self.metawear_r_services[0x11]= create_string_buffer(b'\x11\x80\x00\x02', 4)
        super().setUp()

    def test_disconnected_event(self):
        expected_cmds= [
            [0x0a, 0x02, 0x11, 0x0a, 0xff, 0x02, 0x03, 0x0f],
            [0x0a, 0x03, 0x02, 0x02, 0x1f, 0x00, 0x00, 0x00, 0x32, 0x00, 0x00, 0x00, 0xf4, 0x01, 0x00, 0x00, 0x0a],
            [0x0a, 0x02, 0x11, 0x0a, 0xff, 0x02, 0x01, 0x01],
            [0x0a, 0x03, 0x01]
        ]

        pattern= LedPattern(high_time_ms = 50, pulse_duration_ms = 500, high_intensity = 31, repeat_count = 10)
        event= self.libmetawear.mbl_mw_settings_get_disconnect_event(self.board)

        self.libmetawear.mbl_mw_event_record_commands(event)
        self.libmetawear.mbl_mw_led_write_pattern(self.board, byref(pattern), LedColor.BLUE)
        self.libmetawear.mbl_mw_led_play(self.board)
        self.libmetawear.mbl_mw_event_end_record(event, self.commands_recorded_fn)
        self.events["event"].wait()

        self.assertEqual(self.command_history, expected_cmds)

    def test_battery_state_data_null(self):
        signal= self.libmetawear.mbl_mw_settings_get_battery_state_data_signal(self.board)
        self.assertEqual(signal, None)

class TestSettingsRevision3(TestMetaWearBase):
    def setUp(self):
        self.metawear_r_services[0x11]= create_string_buffer(b'\x11\x80\x00\x03', 4)
        super().setUp()

    def test_disconnected_event(self):
        expected_cmds= [
            [0x0a, 0x02, 0x11, 0x0a, 0xff, 0x08, 0x01, 0x04],
            [0x0a, 0x03, 0xf8, 0xb8, 0x0b, 0x00]
        ]

        event= self.libmetawear.mbl_mw_settings_get_disconnect_event(self.board)

        self.libmetawear.mbl_mw_event_record_commands(event)
        self.libmetawear.mbl_mw_haptic_start_motor(self.board, 100.0, 3000)
        self.libmetawear.mbl_mw_event_end_record(event, self.commands_recorded_fn)
        self.events["event"].wait()
        
        self.assertEqual(self.command_history, expected_cmds)

    def test_read_battery_state(self):
        expected= [0x11, 0xcc]

        battery_signal= self.libmetawear.mbl_mw_settings_get_battery_state_data_signal(self.board)
        self.libmetawear.mbl_mw_datasignal_read(battery_signal)
        self.assertEqual(self.command, expected)

    def test_read_battery_component(self):
        expected_cmds= [
            [0x11, 0xcc],
            [0x11, 0x8c]
        ]

        signal= self.libmetawear.mbl_mw_settings_get_battery_state_data_signal(self.board)
        voltage = self.libmetawear.mbl_mw_datasignal_get_component(signal, Const.SETTINGS_BATTERY_VOLTAGE_INDEX)
        charge = self.libmetawear.mbl_mw_datasignal_get_component(signal, Const.SETTINGS_BATTERY_CHARGE_INDEX)

        self.libmetawear.mbl_mw_datasignal_subscribe(charge, self.sensor_data_handler)
        self.libmetawear.mbl_mw_datasignal_read(voltage)
        self.libmetawear.mbl_mw_datasignal_read(charge)

        self.assertEqual(self.command_history, expected_cmds)

    def test_battery_state_component_data(self):
        tests= [
            {
                'expected': 4148,
                'index': Const.SETTINGS_BATTERY_VOLTAGE_INDEX,
                'name': 'voltage'
            },
            {
                'expected': 99,
                'index': Const.SETTINGS_BATTERY_CHARGE_INDEX,
                'name': 'charge'
            }
        ]

        signal= self.libmetawear.mbl_mw_settings_get_battery_state_data_signal(self.board)
        for test in tests:
            with self.subTest(odr= test['name']):
                component = self.libmetawear.mbl_mw_datasignal_get_component(signal, test['index'])
                self.libmetawear.mbl_mw_datasignal_subscribe(component, self.sensor_data_handler)
                self.notify_mw_char(create_string_buffer(b'\x11\x8c\x63\x34\x10', 5))                
                self.assertEqual(self.data_uint32.value, test['expected'])

    def test_battery_state_data(self):
        expected= BatteryState(voltage= 4148, charge= 99)

        signal= self.libmetawear.mbl_mw_settings_get_battery_state_data_signal(self.board)
        self.libmetawear.mbl_mw_datasignal_subscribe(signal, self.sensor_data_handler)
        self.notify_mw_char(create_string_buffer(b'\x11\x8c\x63\x34\x10', 5))

        self.assertEqual(self.data_battery_state, expected)

class TestSettingsRevision6(TestSettings):
    def setUp(self):
        self.metawear_r_services[0x11]= create_string_buffer(b'\x11\x80\x00\x06', 4)
        super().setUp()

    def test_set_ad_interval(self):
        expected= [0x11, 0x02, 0x9b, 0x02, 0x00, 0x0]
        self.libmetawear.mbl_mw_settings_set_ad_interval(self.board, 417, 0)
        self.assertEqual(self.command, expected)
