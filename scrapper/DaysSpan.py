
import datetime



class DaysSpan:

    def __init__(self, first, last=None):
        if last == None:
            parts = first.split(":")
            if len(parts) == 1:
                last = first
            elif len(parts) == 2:
                first = parts[0]
                last = parts[1]
            else:
                raise ValueError("Range format is YYYY-MM-DD:YYYY-MM-DD")

        self.first = self.str_to_date(first)
        self.last = self.str_to_date(last)

        if self.first > self. last:
            t = self.last
            self.last = self.first
            self.first = t

        self.days = self.get_days()

    def get_days(self):
        days = []
        current = self.first
        one_day = datetime.timedelta(days=1)
        while current <= self.last:
            days.append(current)
            current += one_day

        return days

    def str_to_date(self, s):
        if s == None or len(s) == 0:
            raise ValueError( "Date cannot be null or empty")
        parts = list(map(int, s.split("-")))
        if len(parts) != 3:
            raise ValueError("Date needs to be in YYYY-MM-DD format")

        return datetime.date(parts[0], parts[1], parts[2])

    def format_date(self, d):
        return d.isoformat()[:10]

    def __repr__(self):
        if self.first == self.last:
            return self.format_date(self.first)
        else:
            return "%s to %s (%s days)" % ( self.format_date(self.first), self.format_date(self.last), len(self))




