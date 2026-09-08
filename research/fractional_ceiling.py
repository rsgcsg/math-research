"""Exact algebraic calibration of the explicit T023 density construction."""
from fractions import Fraction as F
from exact_geometry import field,add,sub,mul,distance_squared,ZERO


def verify():
    half,quarter=field(F(1,2)),field(F(1,4))
    sqrt3quarter=field(0,F(1,4))
    def neg(x):
        return tuple(-a for a in x)
    vertices=[(half,ZERO),(sqrt3quarter,quarter),(quarter,sqrt3quarter),
              (ZERO,half),(neg(quarter),sqrt3quarter),(neg(sqrt3quarter),quarter),
              (neg(half),ZERO),(neg(sqrt3quarter),neg(quarter)),
              (neg(quarter),neg(sqrt3quarter)),(ZERO,neg(half)),
              (quarter,neg(sqrt3quarter)),(sqrt3quarter,neg(quarter))]
    assert len(set(vertices))==12
    twice_area=ZERO
    for p,q in zip(vertices,vertices[1:]+vertices[:1]):
        assert distance_squared(p,(ZERO,ZERO))==field(F(1,4))
        cross=sub(mul(p[0],q[1]),mul(p[1],q[0]))
        assert cross==field(F(1,8))
        twice_area=add(twice_area,cross)
    assert twice_area==field(F(3,2))
    cell_area=field(0,2)
    density=field(0,F(1,8))
    total_mass=field(0,F(8,3))
    assert mul(cell_area,density)==field(F(3,4))
    assert mul(density,total_mass)==field(1)
    assert sub(field(25),mul(total_mass,total_mass))==field(F(11,3))
    return dict(polygon_vertices=12,polygon_area='3/4',period_cell_area='2 sqrt(3)',
                independent_set_density='sqrt(3)/8',fractional_total_mass='8/sqrt(3)',
                strict_mass_bound=5)
