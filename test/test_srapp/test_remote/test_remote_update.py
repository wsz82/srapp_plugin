import datetime

from srapp_model.remote.remote_update import make_valid_id, _parse_time


def test_id_transformed_to_valid_id_not_changed():
    assert make_valid_id('D1') == 'D1'


def test_id_transformed_to_valid_id_changed():
    assert make_valid_id('D2/Pzm3') == 'D2**Pzm3'


def test_time_is_parsed():
    t: datetime.datetime = datetime.datetime.now()
    time_without_nanoseconds = datetime.datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)
    time_str: str = str(time_without_nanoseconds)
    parsed_time = _parse_time(time_str)
    assert parsed_time == time_without_nanoseconds
