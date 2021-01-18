import datetime as dt


def year(request):
    year_now = dt.date.today().year
    year_now = str(year_now)
    return {'year_now': year_now}
