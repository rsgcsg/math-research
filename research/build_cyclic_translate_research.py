"""Produce T140/E112 actual-field probes; a separate checker replays the cover."""
from pathlib import Path
import argparse
import json
import time
from cyclic_translate_contacts import contacts
from cyclic_translate_field16 import Element, U, valuation
from verify_quintic_tau_union import verify as geometry

PAIRS=[(233,239),(5557,238),(31,193),(32,36),(0,2),(119,161),
       (230,232),(467,468),(3533,3535),(4,5),(31,118),(232,900)]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();root=Path(__file__).resolve().parents[1]
    started=time.monotonic();report,ctx=geometry(root,geometry_context=True)
    coordinates=ctx['ring']['coordinates']
    rows=[]
    for pos,(i,j) in enumerate(PAIRS):
        a,b=Element(tuple(coordinates(ctx['points'][i]))),Element(tuple(coordinates(ctx['points'][j])))
        result=contacts(a,b,Element.scalar(1),U,lambda z:z.bar(),valuation)
        rows.append(dict(source_indices=[i,j],kind='unit_translation',translation=Element.scalar(1).serial(),result=result))
        N=(1,2,7,37)[pos%4]
        guided=a*U**N-b-Element.scalar(1)
        if guided==Element.scalar(0): raise ValueError('degenerate guided translation')
        guided_result=contacts(a,b,guided,U,lambda z:z.bar(),valuation)
        assert ([N,0] in guided_result['points'] or any(A*N==C for A,B,C in guided_result['lines']))
        rows.append(dict(source_indices=[i,j],kind='forced_one_contact',power=N,translation=guided.serial(),result=guided_result))
        print(i,j,len(result['points']),result['lines'],round(time.monotonic()-started,2),flush=True)
    data=dict(schema='cyclic-translate-research-v1',experiment='E112',
              base_commit='ed4cfb044164b5d88413a2d53c7e030274d04bb8',
              geometry=report['geometry'],u=U.serial(),valuation_u=valuation(U),cases=rows,
              scope='Complete translated cyclic contacts for twelve selected actual Y seed pairs, each at two specified translations; not all Y pairs, not rank-two H-prime, and not a coloring obstruction.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':main()
