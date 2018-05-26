
class Duration(object):
    def __init__(self,
            ticks=None,
            flt=None,
            quarters=None,
            sixteenths=None,
            ticks_per_quarter=24,
            quarters_per_minute=None,
        ):

        self.ticks = ticks
        self.float = flt
        self.quarters = quarters
        self.sixteenths = sixteenths
        self.ticks_per_quarter = ticks_per_quarter
        self.quarters_per_minute = quarters_per_minute
        self.remaining_ticks = 0

        if self.ticks != None:
            self.set_from_ticks(self.ticks)
        elif self.float != None:
            self.set_from_float(self.float)
        elif self.quarters != None and self.sixteenths != None:
            self.set_from_quarters_and_sixteenths(self.quarters, self.sixteenths)

        self.seconds = None
        if self.quarters_per_minute != None:
            self.set_real_time(self.quarters_per_minute)

    def set_from_ticks(self, ticks):
        self.float = self.tick_to_float(ticks)
        self.quarters, self.sixteenths, self.remaining_ticks = self.ticks_to_quarters_and_sixteenths(ticks)

    def set_from_float(self, flt):
        self.float = flt
        self.ticks = self.float_to_tick(flt)
        self.quarters, self.sixteenths, self.remaining_ticks = self.ticks_to_quarters_and_sixteenths(self.ticks)

    def set_from_quarters_and_sixteenths(self, quarters, sixteenths=0, remaining_ticks=0):
        self.quarters = quarters
        self.sixteenths = sixteenths
        self.remaining_ticks = remaining_ticks
        self.ticks_per_sixteenth = self.ticks_per_quarter * 4

        self.ticks = (quarters * self.ticks_per_quarter) + (sixteenths * self.ticks_per_sixteenth) + remaining_ticks

        self.float = self.tick_to_float(self.ticks)

    def float_to_tick(self, flt, ticks_per_quarter=None):
        if not ticks_per_quarter:
            ticks_per_quarter = self.ticks_per_quarter
        return int(round(float(flt) * ticks_per_quarter))

    def tick_to_float(self, tick, ticks_per_quarter=None):
        if not ticks_per_quarter:
            ticks_per_quarter = self.ticks_per_quarter
        return float(tick) / ticks_per_quarter

    def ticks_to_quarters_and_sixteenths(self, ticks, ticks_per_quarter=None):
        if not ticks_per_quarter:
            ticks_per_quarter = self.ticks_per_quarter
        quarters, remainder = divmod(ticks, ticks_per_quarter)
        sixteenths, remaining_ticks = divmod(remainder, ticks_per_quarter * 4)
        return quarters, sixteenths, remaining_ticks

    def quarters_and_sixteenths_to_ticks(self, quarters, sixteenths, ticks_per_quarter=None):
        if not ticks_per_quarter:
            ticks_per_quarter = self.ticks_per_quarter
        ticks = quarters * ticks_per_quarter
        ticks = ticks + (sixteenths * (ticks_per_quarter / 4))
        return ticks

    def set_real_time(self, quarters_per_minute):
        self.quarters_per_minute = float(quarters_per_minute)
        self.ticks_per_minute = self.quarters_per_minute * self.ticks_per_quarter
        self.tick_duration_in_seconds = 60.0 / self.ticks_per_minute
        self.seconds = self.tick_duration_in_seconds * self.ticks
