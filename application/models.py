from application.extensions import db


class DateModel(db.Model):
    __abstract__ = True

    entry_date = db.Column(db.Date, default=db.func.current_date())
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    def as_dict(self):
        return {
            "entry-date": self.entry_date,
            "start-date": self.start_date,
            "end-date": self.end_date,
        }
