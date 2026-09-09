"""Small rational calibration of T066; the arbitrary-field statement is proved on paper."""
from fractions import Fraction as F
import json


def verify():
    c0, s0, c1, s1, d = F(5, 8), F(0), F(0), F(1, 8), F(39)
    t0, t1 = (F(-83, 84), F(5, 8)), (F(-1, 40), F(-1, 12))
    q, p = (F(2, 3), F(-1, 5)), (F(-4, 7), F(1, 2))
    assert c0*c0+s0*s0+d*(c1*c1+s1*s1) == 1
    assert c0*c1+s0*s1 == 0
    determinant = c1*c1+s1*s1
    assert determinant == F(1, 64)
    recovered = ((-c1*t1[0]-s1*t1[1])/determinant,
                 (s1*t1[0]-c1*t1[1])/determinant)
    assert recovered == q
    assert (c1*q[0]-s1*q[1]+t1[0], s1*q[0]+c1*q[1]+t1[1]) == (0, 0)
    assert (c0*q[0]-s0*q[1]+t0[0], s0*q[0]+c0*q[1]+t0[1]) == p
    template = ((0, 0), (1, 0), (0, 1))
    for x, y in template:
        assert (c1*x-s1*y+t1[0], s1*x+c1*y+t1[1]) != (0, 0)
    assert 39 not in {1, 3, 5, 11, 15, 33, 55, 165}
    return dict(status='PASS', virtual_source=list(map(str, q)), virtual_target=list(map(str, p)),
                moving_points_outside_K=3,
                scope='Written T066 classifies all real quadratic poses; this example claims no contact rank or chromatic lower bound')


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Assertions must be enabled')
    print(json.dumps(verify(), indent=2))
