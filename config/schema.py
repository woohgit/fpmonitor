from configglue.schema import BoolOption, IntOption, StringOption, Schema, Section


class SettingsSchema(Schema):
    project_dir = StringOption(fatal=True)
    shared_secret = StringOption(fatal=True, raw=True)
    test_mode = BoolOption(default=False)
    node_user_id = IntOption(default=0)
    node_name = StringOption(default="")

    class fpmonitor(Section):
        environment = StringOption(default="production")
