from configglue.schema import StringOption, Schema, Section


class SettingsSchema(Schema):
    project_dir = StringOption(fatal=True)
    shared_secret = StringOption(fatal=True, raw=True)

    class fpmonitor(Section):
        environment = StringOption(default="production")
