"""Page registry - add a new view module here to make it appear in the sidebar."""
from . import (assistant, home, boq, cashflow, contractor, costs, drawings, forecast, materials, mrs, overview, rent, report,
               responsibility, sheets, solar)

PAGES = [home, overview, assistant, contractor, rent, costs, cashflow, boq, mrs, solar, forecast, responsibility, drawings,
         materials, report, sheets]
