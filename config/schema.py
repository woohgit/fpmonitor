from configglue.schema import BoolOption, IntOption, StringOption, Schema, Section


class SettingsSchema(Schema):
    project_dir = StringOption(fatal=True)
    shared_secret = StringOption(fatal=True, raw=True)

    class fpmonitor(Section):
        environment = StringOption(default="production")

    class client(Section):
        node_user_id = IntOption(default=0)
        node_name = StringOption(default="")  # should be unique per user
        server_host = StringOption(fatal=True)  # this is the monitoring server URL

    class server(Section):
        test_mode = BoolOption(default=False)
        alert_info_load = IntOption(default=2)
        alert_info_seen = IntOption(default=2)
        alert_info_memory = IntOption(default=80)
        alert_warning_load = IntOption(default=3)
        alert_warning_seen = IntOption(default=4)
        alert_warning_memory = IntOption(default=90)
        alert_danger_load = IntOption(default=8)
        alert_danger_seen = IntOption(default=4)
        alert_danger_memory = IntOption(default=95)
        notification_level = IntOption(default=0)
