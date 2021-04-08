from app.models.type import RoomType
from app.models.chat import Room
from app.models.user import User
from app.models.function import kstnow
from app import db

class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    total_budget = db.Column(db.Integer, nullable=False)
    current_budget = db.Column(db.Integer, nullable=False)
    start_at = db.Column(db.DateTime())
    close_at = db.Column(db.DateTime())
    banner_image = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=False)
    hongbo_image = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

    club_head = db.relationship('ClubHead', backref='club')
    rooms = db.relationship('Room', backref='club', lazy='dynamic')
    majors = db.relationship('Major', backref='club')

    def __lt__(self, operand):
        try:
            boolean = self.name < operand.name
        except TypeError:
            boolean = False
        return boolean

    def get_all_applicant_room(self):
        '''
        모든 동아리 신청자 반환하는 메서드
        '''
        return Room.query.filter_by(club_id=self.id).filter(Room.status != RoomType.C.name).filter(Room.status != RoomType.N.name).all()
    
    def is_recruiting(self):
        '''
        모집 기간인지 확인하는 메서드
        처음 100번째줄 if 문 코드는 공고한적 없는 동아리의 경우 False를 반환한다.
        '''
        if self.start_at == None or self.close_at == None:
            return False
        return kstnow() >= self.start_at and kstnow() <= self.close_at 

    def __repr__(self):
        return '<Club> {}>'.format(self.name)


class ClubHead(db.Model):
    __tablename__ = 'club_head'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id', ondelete='CASCADE'))

    def __repr__(self):
        return '<ClubHead> {},{}'.format(self.user.name, self.club.name)


class ClubMember(db.Model):
    __tablename__ = 'club_member'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))

    def __repr__(self):
        return '<Application> {},{}'.format(User.query.get(self.user_id).name, Club.query.get(self.club_id).name)


class Major(db.Model):
    __tablename__ = 'major'
    id = db.Column(db.Integer, primary_key=True)
    major_name = db.Column(db.String(45))
    club_id = db.Column(db.Integer, db.ForeignKey("club.id"))
