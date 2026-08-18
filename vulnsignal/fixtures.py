from .experiment import TriageObservation
from .models import Finding


def synthetic_findings() -> list[Finding]:
    rows = [
        ("F01",1,1,"critical","critical",.96,"CWE-89","api/orders.py","unsanitized order lookup sql injection",.95,.90,.95,1,1,1,1,8,3.5),
        ("F02",1,1,"high","critical",.88,"CWE-89","api/orders.py","sql injection in order lookup query",.86,.80,.95,1,1,1,1,11,4.0),
        ("F03",1,1,"high","high",.91,"CWE-798","config/auth.py","hard coded service credential",.92,.85,.90,1,1,1,1,6,2.0),
        ("F04",1,0,"medium","none",.64,"CWE-22","utils/path.py","possible path traversal in normalized temp path",.45,.35,.30,0,0,0,0,25,-1),
        ("F05",1,1,"high","medium",.82,"CWE-79","web/render.py","stored xss in admin note rendering",.78,.72,.65,1,1,1,1,14,8.0),
        ("F06",0,1,"none","high",.31,"CWE-352","web/settings.py","csrf protection missing on email change",.60,.55,.70,0,0,0,0,-1,-1),
        ("F07",1,1,"critical","high",.93,"CWE-918","services/fetch.py","server side request forgery in url fetcher",.90,.82,.85,1,1,1,1,9,5.0),
        ("F08",1,0,"high","none",.73,"CWE-200","api/profile.py","response may expose internal identifier",.50,.40,.35,0,0,0,0,19,-1),
        ("F09",0,0,"none","none",.12,"CWE-000","docs/readme.md","no vulnerability",.10,.10,.10,0,0,0,0,-1,-1),
        ("F10",1,1,"medium","medium",.79,"CWE-862","api/reports.py","authorization check missing on report export",.84,.78,.80,1,1,1,1,12,6.5),
        ("F11",1,1,"medium","medium",.77,"CWE-862","api/reports.py","report export lacks authorization guard",.80,.74,.80,1,1,0,0,16,-1),
        ("F12",0,1,"none","low",.28,"CWE-209","api/errors.py","verbose error leaks stack metadata",.52,.48,.30,0,0,0,0,-1,-1),
    ]
    return [Finding(*row) for row in rows]


def synthetic_triage_experiment() -> tuple[list[TriageObservation], list[TriageObservation]]:
    control = [
        TriageObservation(f"C{i}", "raw", completed, accepted, remediated, minutes)
        for i, (completed, accepted, remediated, minutes) in enumerate([
            (1,1,1,28),(1,1,0,34),(1,0,0,41),(1,1,1,24),(0,0,0,52),(1,1,0,30),(1,0,0,37),(1,1,1,26),(0,0,0,48),(1,1,0,31)
        ], 1)
    ]
    treatment = [
        TriageObservation(f"T{i}", "enriched", completed, accepted, remediated, minutes)
        for i, (completed, accepted, remediated, minutes) in enumerate([
            (1,1,1,12),(1,1,1,15),(1,1,0,19),(1,1,1,11),(1,0,0,18),(1,1,1,14),(1,1,0,16),(1,1,1,13),(1,1,0,17),(1,1,1,12)
        ], 1)
    ]
    return control, treatment
