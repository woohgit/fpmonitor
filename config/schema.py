from configglue.schema import BoolOption, StringOption, Schema, Section


class SettingsSchema(Schema):
    project_dir = StringOption(fatal=True)
    shared_secret = StringOption(fatal=True, raw=True)
    test_mode = BoolOption(default=False)

    class fpmonitor(Section):
        environment = StringOption(default="production")
