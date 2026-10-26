"""Wrong-action defence: the app must not send anything to an employer or a third party.

The only write endpoints are the analysis itself and the local budget reset.
If someone adds an endpoint that posts outward, this test fails.
"""

from server import app

ALLOWED_WRITES = {"/api/analyze", "/api/budget/reset"}


def test_only_local_write_endpoints_exist():
    writes = {
        route.path
        for route in app.routes
        if getattr(route, "methods", None) and ({"POST", "PUT", "PATCH", "DELETE"} & route.methods)
    }
    assert writes == ALLOWED_WRITES
