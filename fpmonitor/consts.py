STATUS_OK = 0
STATUS_UNKNOWN = 1
STATUS_INFO = 2
STATUS_WARNING = 3
STATUS_ERROR = 4
STATUS_CHOICES = (
    (STATUS_OK, 'success'),
    (STATUS_UNKNOWN, ''),
    (STATUS_INFO, 'info'),
    (STATUS_WARNING, 'warning'),
    (STATUS_ERROR, 'danger'),
)
