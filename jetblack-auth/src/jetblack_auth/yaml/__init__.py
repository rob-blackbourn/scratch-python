def initialize_types():
    from .time_handler import add_custom_time
    from .timedelta_handler import add_custom_type_timedelta
    add_custom_time()
    add_custom_type_timedelta()