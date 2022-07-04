from typing import Dict, Set

from model.m_field import FieldConstraint

SHEARS_TODO_LAYER_STR = 'sciecia_do_zrobienia'
BOREHOLES_LAYER_STR = 'wiercenia'
BOREHOLE_PERSONS_LAYER_STR = 'wiercenia_wykonawcy'
LAYERS_LAYER_STR = 'wiercenia_warstwy'
DRILLED_WATER_LAYER_STR = 'woda_nawiercona'
SET_WATER_LAYER_STR = 'woda_ustalona'
EXUDATIONS_LAYER_STR = 'wysieki'
PROBES_LAYER_STR = 'sondowania'
PROBE_UNITS_LAYER_STR = 'sondowania_wartosci'
PROBE_PERSONS_LAYER_STR = 'sondowania_wykonawcy'
SHEAR_UNITS_LAYER_STR = 'sciecia_wartosci'
TEAMS_LAYER_STR = 'zespoły'
POINTS_LAYER_STR = 'punkty'

LAYER_NAME_TO_FIELDS_CONSTRAINTS: Dict[str, Dict[int, Set[FieldConstraint]]] = {
    POINTS_LAYER_STR: {
        2: {FieldConstraint.NOT_NULL, FieldConstraint.UNIQUE},
        6: {FieldConstraint.STATUS},
        7: {FieldConstraint.STATUS},
    },
    BOREHOLES_LAYER_STR: {
        2: {FieldConstraint.NOT_NULL, FieldConstraint.UNIQUE}},
    PROBES_LAYER_STR: {
        2: {FieldConstraint.NOT_NULL, FieldConstraint.UNIQUE},
        8: {FieldConstraint.NOT_NULL}},
    TEAMS_LAYER_STR: {
        2: {FieldConstraint.NOT_NULL, FieldConstraint.UNIQUE}},
    SHEARS_TODO_LAYER_STR: {1: {FieldConstraint.NOT_NULL},
                            2: {FieldConstraint.NOT_NULL}},
    BOREHOLE_PERSONS_LAYER_STR: {1: {FieldConstraint.NOT_NULL},
                                 2: {FieldConstraint.NOT_NULL}},
    PROBE_PERSONS_LAYER_STR: {1: {FieldConstraint.NOT_NULL},
                              2: {FieldConstraint.NOT_NULL}},
    LAYERS_LAYER_STR: {1: {FieldConstraint.NOT_NULL},
                       3: {FieldConstraint.SOIL},
                       4: {FieldConstraint.SOIL},
                       5: {FieldConstraint.SOIL},
                       },
    DRILLED_WATER_LAYER_STR: {1: {FieldConstraint.NOT_NULL},
                              2: {FieldConstraint.NOT_NULL, FieldConstraint.WATER_HORIZON},
                              3: {FieldConstraint.NOT_NULL}},
    SET_WATER_LAYER_STR: {1: {FieldConstraint.NOT_NULL},
                          2: {FieldConstraint.NOT_NULL, FieldConstraint.WATER_HORIZON},
                          3: {FieldConstraint.NOT_NULL}},
    EXUDATIONS_LAYER_STR: {1: {FieldConstraint.NOT_NULL},
                           2: {FieldConstraint.NOT_NULL, FieldConstraint.EXUDATION},
                           3: {FieldConstraint.NOT_NULL}},
    PROBE_UNITS_LAYER_STR: {1: {FieldConstraint.NOT_NULL},
                            2: {FieldConstraint.NOT_NULL},
                            3: {FieldConstraint.NOT_NULL}},
    SHEAR_UNITS_LAYER_STR: {1: {FieldConstraint.NOT_NULL},
                            2: {FieldConstraint.NOT_NULL},
                            3: {FieldConstraint.NOT_NULL, FieldConstraint.SHEARS_NUMBER},
                            4: {FieldConstraint.NOT_NULL}},
}
