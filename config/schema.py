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
