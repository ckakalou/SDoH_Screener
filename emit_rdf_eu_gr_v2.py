"""Emit RDF (Turtle) from SDoH responses using an ontology mapping (EU/GR v2).

Usage:
  pip install rdflib
  python emit_rdf_eu_gr_v2.py --responses responses.json --mapping sdoh_ontology_mapping_eu_gr_v2.json --out sdoh_out.ttl [--results results.json]
"""

import json, argparse, uuid
from datetime import datetime
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD

def load_json(p):
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

def nsbuild(ctx): 
    return {k: Namespace(v) for k, v in ctx.items()}

def iri(ns, curie_or_iri: str):
    if '://' in curie_or_iri:
        return URIRef(curie_or_iri)
    if ':' in curie_or_iri:
        p, local = curie_or_iri.split(':', 1)
        return ns[p][local]
    return ns['healie'][curie_or_iri]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--responses', required=True)
    ap.add_argument('--mapping', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--results', required=False)
    args = ap.parse_args()

    resp = load_json(args.responses)
    results = load_json(args.results) if args.results else {}
    m = load_json(args.mapping)
    ns = nsbuild(m['@context'])

    g = Graph()
    for p, space in ns.items():
        g.bind(p, space)

    person_id = resp.get('person_id') or str(uuid.uuid4())
    person = ns['person'][person_id]
    g.add((person, RDF.type, iri(ns, m['classes']['Person'])))
    g.add((person, RDFS.label, Literal(f'Person {person_id}')))

    qidx = {q['id']: q for q in m['questions']}

    for qid, val in resp.items():
        if qid not in qidx:
            continue
        qinfo = qidx[qid]
        qnode = URIRef(qinfo['question_iri'])
        ans = ns['ans'][f'{person_id}-{qid}']

        g.add((ans, RDF.type, iri(ns, m['classes']['Answer'])))
        g.add((ans, iri(ns, m['predicates']['ofQuestion']), qnode))
        g.add((ans, iri(ns, m['predicates']['forPerson']), person))
        g.add((ans, iri(ns, m['predicates']['answeredAt']), Literal(datetime.utcnow().isoformat(), datatype=XSD.dateTime)))

        if isinstance(val, list):
            for item in val:
                ve = (qinfo.get('value_set') or {}).get(str(item))
                if ve:
                    g.add((ans, iri(ns, m['predicates']['hasCode']), URIRef(ve['code_iri'])))
            g.add((ans, iri(ns, m['predicates']['valueJson']), Literal(json.dumps(val), datatype=XSD.string)))
        elif isinstance(val, dict):
            g.add((ans, iri(ns, m['predicates']['valueJson']), Literal(json.dumps(val), datatype=XSD.string)))
        else:
            ve = (qinfo.get('value_set') or {}).get(str(val))
            if ve:
                g.add((ans, iri(ns, m['predicates']['hasCode']), URIRef(ve['code_iri'])))
            g.add((ans, iri(ns, m['predicates']['value']), Literal(str(val))))

    # Attach derived results as literals on the person node (simple, audit-friendly)
    for k, v in results.items():
        pred = ns['healie'][k]
        if isinstance(v, bool):
            g.add((person, pred, Literal(v)))
        elif isinstance(v, (int, float)):
            g.add((person, pred, Literal(v)))
        elif v is None:
            continue
        else:
            g.add((person, pred, Literal(str(v))))

    out = Path(args.out)
    g.serialize(destination=str(out), format='turtle')
    print(f'Wrote RDF to {out}')

if __name__ == '__main__':
    main()
