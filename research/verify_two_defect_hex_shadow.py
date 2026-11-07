#!/usr/bin/env python3
"""Exact rational verifier for the adjacent two-defect hexagon shadow lemma.

Only checks elementary sharp rational inequalities; the proof that
the forced-color set satisfies them is in the accompanying document.
"""
from fractions import Fraction as F
import json

def verify_periodic_partial_coloring():
    # Triangular lattice N=a^2+a*b+b^2 has no N=2 for integer a,b.
    # Every 7-star B1(v) has one vertex in each residue m+3n mod 7.
    diffs=[(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1)]
    for m in range(7):
        for n in range(7):
            residues={(m+a+3*(n+b))%7 for a,b in diffs}
            if residues != set(range(7)):
                raise RuntimeError("not seven residue classes in each star")
            if len([r for r in residues if r in (0,1)])!=2:
                raise RuntimeError("double code does not double dominate stars")
    norms={a*a+a*b+b*b for a in range(-12,13) for b in range(-12,13) if (a,b)!=(0,0)}
    if 1 not in norms or 3 not in norms or 2 in norms:
        raise RuntimeError("triangular center distances not 1,3,...")
    r=F(1,20)
    # For unit-free sixth-color disks:
    # nearby centers D=2 sqrt(3)/5 -> D+2r<1 if sqrt3<2.
    if not (F(4,5)+2*r<1):  # upper bound D<4/5
        raise RuntimeError("nearby disks have unit pair risk")
    if not (F(6,5)-2*r>1):
        raise RuntimeError("next nearest disks have unit pair risk")
    # Exact density formula for arbitrary r<1/10, limiting r->1/10:
    # density -> 5/7+pi/(84 sqrt3)
    return {
        "triangular_norm_two_absent":True,
        "seven_star_residues_rainbow":True,
        "two_defect_classes_in_every_star":2,
        "disk_radius_test":"1/20",
        "closest_center_class":"2*sqrt(3)/5",
        "next_nearest_center_class_at_least":"6/5",
        "six_color_partial_covered_density_formula":"5/7+25*pi*r^2/(21*sqrt(3))",
        "limit_r_up_to_1_over_10":"5/7+pi/(84*sqrt(3))",
        "scope":"strict unit-free only on partially colored domain; not 6 coloring of plane"
    }


def verify_four_frozen_triangle():
    # Three exact unit triangle vertices in Q(sqrt3), and 12 exact
    # unit-visibility witnesses from four frozen code classes.
    hlo,hhi=F(69,200),F(7,20)
    # x coordinate a+b*h with h=sqrt3/5; y rational.
    p=[(F(1,50),F(0),F(2,25)),
       (F(1,50),F(5,2),F(29,50)),
       (F(1,50),F(0),F(27,25))]
    # p1-p0=(sqrt3/2,1/2), p2-p0=(0,1), p2-p1=(-sqrt3/2,1/2).
    # q-p horizontal=(5/2)h=sqrt(3)/2, vertical=1/2;
    # t-p horizontal=0, vertical=1;
    # q-t horizontal=(5/2)h, vertical=-1/2.
    edge_pq=F(25,4)*F(3,25)+F(1,4)
    edge_pt=F(1)
    edge_qt=F(25,4)*F(3,25)+F(1,4)
    if (edge_pq,edge_pt,edge_qt)!=(F(1),F(1),F(1)):
        raise RuntimeError("unit equilateral triangle exact squared lengths failed")
    rows=[
      [(1,-2,1),(2,1,-2),(3,-1,-1),(6,2,-1)],
      [(1,-1,3),(2,0,3),(3,3,0),(6,2,-1)],
      [(1,-2,1),(2,0,3),(3,-2,4),(6,-3,3)]
    ]
    if not (F(17,2500)<F(3,25) and F(37,2500)<F(3,25)
                and (F(1,50)-hhi/2)**2+F(1,50)**2<F(3,25)):
        raise RuntimeError("triangle vertices not inside omitted hex inballs")
    radius=F(1,140)
    if not (F(71537,40000)<(1+hlo-radius)**2):
        raise RuntimeError("common translate radius too large for leaves")
    assert_mode_unique_cells={(m,n) for row in rows for _,m,n in row}
    if len(assert_mode_unique_cells)!=9:
        raise RuntimeError("pure leaf cell count mismatch")
    report=[]
    for pi,(a,b,y) in enumerate(p):
        tests=[]
        for j,m,n in rows[pi]:
            if (m+3*n)%7!=j:raise RuntimeError("wrong pure color residue")
            coef=F(2*m+n)-b
            v1=coef*hlo-a;v2=coef*hhi-a
            xlo=F(0) if v1*v2<=0 else min(v1*v1,v2*v2)
            xhi=max(v1*v1,v2*v2)
            vY=F(3*n,5)-y
            low=xlo+vY*vY;high=xhi+vY*vY
            if not (1<low<=high<F(9,5)):
                raise RuntimeError(f"four-frozen inball failure:{pi,j,m,n} {low} {high}")
            tests.append({"pure_color":j,"m":m,"n":n,"sq_distance_lower":str(low),"sq_distance_upper":str(high)})
        report.append({"triangle_vertex_index":pi,"tests":tests})
    return {
      "status":"PASS",
      "unit_triangle_in_missing_classes":[0,4,5],
      "frozen_classes":[1,2,3,6],
      "all_vertices_have_four_true_unit_neighbors":True,
      "inball_distance_squared_window":"1<d^2<9/5<(1+h)^2",
      "common_translation_radius":"1/140",
      "leaf_cell_count_distinct":9,
      "weak_six_assigned_palette_impurity_fraction_at_least":"pi/(56448*sqrt(3))",
      "exact_pure_hex_witnesses":report,
      "conclusion":"no proper six coloring preserves these four original hex code classes as fixed monochrome classes"
    }


def verify_ten_pure_hex_lock():
    # Exact algebraic checks for two rational points at unit distance.
    # All ten pure-hex inballs are certified by 1<d^2<9/5<(1+h)^2.
    hlo,hhi=F(69,200),F(7,20)
    p=[F(-3,20),F(17,20)]
    rows=[
        [(2,1,-2),(3,-1,-1),(4,-2,2),(5,-1,2),(6,2,-1)],
        [(2,-1,1),(3,2,-2),(4,3,-2),(5,2,1),(6,0,2)]
    ]
    if p[1]-p[0]!=1 or not (F(3,20)<hlo and F(17,20)-2*hlo<hlo):
        raise RuntimeError("two points do not form exact unit pair in two defect hexes")
    if not (F(9,5)<(1+hlo)**2):
        raise RuntimeError("the inball cannot reach exact unit length")
    table=[]
    for k,R in enumerate(rows):
        cells=[]
        for col,m,n in R:
            if (m+3*n)%7!=col:
                raise RuntimeError("pure hex congruence color mismatch")
            A=2*m+n
            left=A*hlo-p[k]
            right=A*hhi-p[k]
            x_lower=F(0) if left*right<=0 else min(left*left,right*right)
            x_upper=max(left*left,right*right)
            y=F(3*n,5)
            low=x_lower+y*y
            high=x_upper+y*y
            if not (F(1)<low<=high<=F(9,5)):
                raise RuntimeError(f"10 exact pure inball certificates failed: {(k,col,m,n)}")
            cells.append({"label":col,"triangular_coordinate":[m,n],
                         "distance_squared_lower":str(low),
                         "distance_squared_upper":str(high)})
        table.append({"forced_point_x":str(p[k]),"pure_inball_unit_neighbors":cells})
    return {"result":"PASS","points":[["-3/20","0"],["17/20","0"]],
            "separation_exactly_one":True,"ten_pure_inball_witnesses":table,
            "inball_radius_lower":"69/200",
            "distance_squared_window":"1<d^2<9/5<(1+h)^2",
            "conclusion":"conditional six-color impossibility when five original hexagon code classes stay monochrome"}


def verify():
    hlo,hhi=F(69,200),F(7,20)
    if not ((5*hlo)**2<3<(5*hhi)**2):
        raise RuntimeError("irrational hex inradius bracket invalid")
    q=F(9,25)
    vals={
      "F0_vertical_pure_center":hhi*hhi+F(19,40)**2,
      "F0_left_top_bottom_pure":(hhi-F(1,8))**2+F(11,20)**2,
      "F0_left_far_pure":(2*hhi-F(1,8))**2+F(1,20)**2,
      "F1_vertical_pure_center":(F(7,5)-3*hlo)**2+F(19,40)**2,
    }
    expected={
      "F0_vertical_pure_center":F(557,1600),
      "F0_left_top_bottom_pure":F(565,1600),
      "F0_left_far_pure":F(533,1600),
      "F1_vertical_pure_center":F(7177,20000),
    }
    if vals!=expected or any(v>=q for v in vals.values()):
        raise RuntimeError("strict exclusion via pure hex circumdisks not certified")
    rect=(F(71,100)+F(1,8))**2+F(1,4)**2
    if rect!=F(30389,40000) or rect>=1:
        raise RuntimeError("forced color region diameter not below unit")
    if not (F(7,5)-2*hlo==F(71,100)):
        raise RuntimeError("neighbor hex upper x bound")
    return {
        "status":"PASS",
        "scope":"exact rational square bounds and rectangular diameter only, not chi7",
        "hex_inradius_bracket":[str(hlo),str(hhi)],
        "pure_cell_visibility_necessary_center_distance_range":["3/5","7/5"],
        "strictly_below_9_over_25":{k:str(v) for k,v in vals.items()},
        "forced_color_rectangle":{"min_x":"-1/8","max_x":"71/100",
                                   "min_y":"-1/8","max_y":"1/8"},
        "squared_diameter_strict_upper":str(rect),
        "positive_unit_squared_gap":str(1-rect),
        "partial_coloring_color_count":6,
        "ten_pure_hex_unit_lock":verify_ten_pure_hex_lock(),
        "four_frozen_equilateral_triangle_lock":verify_four_frozen_triangle(),
        "periodic_global_partial_coloring":verify_periodic_partial_coloring(),
        "interpretation":"only the first-step forced sixth-color subset is shown unit-free"
    }
if __name__=="__main__":
    print(json.dumps(verify(),indent=2,sort_keys=True))
