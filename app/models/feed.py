from app import db 

class Feed(db.Model):
    __tablename__ = 'feed'
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("club.id"))
    contents = db.Column(db.String(4001))
    upload_at = db.Column(db.DateTime())
    pin = db.Column(db.Boolean(), default=False)

    club = db.relationship('Club', backref='feed')
    
    def __repr__(self):
        return "<Feed> {} {}".format(self.club, self.contents)
