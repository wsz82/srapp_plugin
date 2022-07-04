from srapp_model.remote.remote_update import make_valid_id


def test_id_transformed_to_valid_id_not_changed():
    assert make_valid_id('D1') == 'D1'


def test_id_transformed_to_valid_id_changed():
    assert make_valid_id('D2/Pzm3') == 'D2**Pzm3'
