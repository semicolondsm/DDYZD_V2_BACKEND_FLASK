import enum
from datetime import datetime
from app import db

class ChatEnum(enum.Enum):
    U = 1  # 유저
    C = 2  # 동아리장
    H1 = 3 # 동아리 지원
    H2 = 4 # 면접 일정
    H3 = 5 # 면접 결과

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    user_looked = db.Column(db.Boolean(), default=False)
    club_looked = db.Column(db.Boolean(), default=False)

    chats = db.relationship('Chat', backref='room', lazy='dynamic')

    def __lt__(self, operand):
        try:
            boolean = self.last_message()[1] < operand.last_message()[1]
        except TypeError:
            boolean = False
        return boolean

    def last_message(self):
        chat = self.chats.order_by(Chat.created_at.desc()).first()
        msg = chat.msg if chat is not None else None
        created_at = chat.created_at if chat is not None else None
        return msg, created_at 

    def json(self, is_user, index=0):
        msg, created_at = self.last_message()
        if is_user:
            club = Club.query.get(self.club_id)
            id = club.club_id
            name = club.club_name
            image = 'https://api.semicolon.live/file/'+club.profile_image
        else:
            user = User.query.get(self.user_id)
            id = user.user_id
            name = user.name
            image = user.image_path
        return {
		    "roomid" : str(self.id),
		    "id" : str(id),
		    "name" : name,
		    "image" : image,
		    "lastdate" :  isoformat(created_at),
		    "lastmessage" : msg,
            "index": index
        }

    def __repr__(self):
        return '<Room> {}'.format(self.id)

class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    title = db.Column(db.String(512))
    msg = db.Column(db.String(512))
    created_at = db.Column(db.DateTime(),  default=datetime.utcnow)
    user_type = db.Column(db.Enum(ChatEnum))

    def json(self):
        return {
            "title": self.title,
            "msg": self.msg,
            "user_type": self.user_type.name,
            "created_at": isoformat(self.created_at)
        }

    def __repr__(self):
        return '<Chat> {}'.format(self.msg)

class Club(db.Model):
    __tablename__ = 'club'
    club_id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(45), nullable=False)
    total_budget = db.Column(db.Integer, nullable=False)
    current_budget = db.Column(db.Integer, nullable=False)
    start_at = db.Column(db.DateTime())
    close_at = db.Column(db.DateTime())
    banner_image = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=False)
    hongbo_image = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

    club_head = db.relationship('ClubHead', backref='club')
    rooms = db.relationship('Room', backref='club')
    majors = db.relationship('Major', backref='club')

    def __lt__(self, operand):
        try:
            boolean = self.club_name < operand.club_name
        except TypeError:
            boolean = False
        return boolean

    def get_all_applicant_room(self):
        '''
        모든 동아리 신청자 반환하는 메서드
        '''
        return Room.query.join(User, Room.user_id==User.user_id).join(Application, User.user_id==Application.user_id).filter_by(club_id=self.club_id, result=False).all()

    def is_recruiting(self):
        '''
        모집 기간인지 확인하는 메서드
        처음 100번째줄 if 문 코드는 공고한적 없는 동아리의 경우 False를 반환한다.
        '''
        if self.start_at == None or self.close_at == None:
            return False
        return datetime.now() >= self.start_at and datetime.now() <= self.close_at 

    def __repr__(self):
        return '<Club> {}>'.format(self.club_name)

class ClubHead(db.Model):
    __tablename__ = 'club_head'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id', ondelete='CASCADE'))

    def __repr__(self):
        return '<ClubHead> {},{}'.format(self.club_head_user.name, self.club.club_name)

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    gcn = db.Column(db.String(5))
    image_path = db.Column(db.String(45))
    github_url = db.Column(db.String(45))
    email = db.Column(db.String(50))
    device_token = db.Column(db.String(4096))
    bio = db.Column(db.String(256))
    
    rooms = db.relationship('Room', backref='user', lazy='dynamic')
    club_heads = db.relationship('ClubHead', backref='club_head_user')
    applicants = db.relationship('Application', backref='user')

    def get_clubs(self):
        '''
        내가 동아리장인 동아리들 이름 출력하는 메서드
        '''
        clubs = []
        for ch in self.club_heads:
            clubs.append(Club.query.get_or_404(ch.club_id)) 
        try:
            clubs.sort()
        except TypeError:
            clubs = []
        return clubs

    def is_user(self, room):
        '''
        내가 채팅방의 일반 유저인지 확인하는 메서드
        '''
        return self.user_id == room.user_id
  
    def is_clubhead(self, club=None, room=None):
        '''
        내가 채팅방 혹은 동아리의 동아리장인지 확인하는 메서드
        '''
        club_head = None
        if room is not None:
            club_head = ClubHead.query.filter_by(user_id=self.user_id, club_id=room.club_id).first()
        if club is not None:
            club_head = ClubHead.query.filter_by(user_id=self.user_id, club_id=club.club_id).first()
       
        return club_head is not None

    def is_applicant(self, club, result=False):
        '''
        내가 동아리에 신청했는지 아는 메서드
        result가 False이면 신청중인 사람,
        result가 True이면 동아리에 합격한 사람
        '''
        return Application.query.filter_by(user_id=self.user_id, club_id=club.club_id, result=result).first()

    def is_member(self, club=None, room=None):
        '''
        내가 동아리의 맴버인지 아는 메서드
        '''
        if club is not None:
            if self.is_clubhead(club=club):
                return True
            if self.is_applicant(club=club, result=True):
                return True
            return False
        if room is not None:
            if self == room.user:
                return True
            if room.club.club_head[0].user_id == self.user_id:
                return True
            return False


    def __repr__(self):
        return '<User> {},{}'.format(self.name, self.gcn)

class Application(db.Model):
    __tablename__ = 'application'
    application_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    result = db.Column(db.Boolean(), nullable=True)

class Major(db.Model):
    __tablename__ = 'major'
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("club.club_id"))
    major_name = db.Column(db.String(45))


def isoformat(date):
    try:
        date = date.isoformat()+'.000+09:00'
    except AttributeError:
        date = None
    return date