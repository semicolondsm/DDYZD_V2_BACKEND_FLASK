from app.models.type import RoomType
from app.models.club import Room
from app import db
from flask_socketio import rooms

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    gcn = db.Column(db.String(5))
    image_path = db.Column(db.String(45))
    github_url = db.Column(db.String(45))
    email = db.Column(db.String(50))
    device_token = db.Column(db.String(4096))
    bio = db.Column(db.String(256))
    mobile_session_id = db.Column(db.String(255), default='0')
    desktop_session_id = db.Column(db.String(255), default='0')

    rooms = db.relationship('Room', backref='user', lazy='dynamic')
    club_heads = db.relationship('ClubHead', backref='user')
    club_members = db.relationship('ClubMember', backref='user', lazy='dynamic')

    def get_clubs(self):
        '''
        내가 동아리장인 동아리들 이름 출력하는 메서드
        '''
        clubs = []
        from app.models.club import Club
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
        return self.id == room.user_id
  
    def is_clubhead(self, club):
        '''
        내가 채팅방 혹은 동아리의 동아리장인지 확인하는 메서드
        '''
        from app.models.club import ClubHead
        return ClubHead.query.filter_by(user_id=self.id, club_id=club.id).first()

    def is_applicant(self, club):
        '''
        내 방이 applicant 상태인지 아는 에서드
        '''
        room_query = Room.query.filter_by(user_id=self.id).filter_by(club_id=club.id)
        from app import logger
        logger.info("BES"+str(Room.query.all()[1].status))
        return room_query.filter(Room.status==RoomType.A.name).first()

    def is_scheduled(self, club):
        '''
        내 방이 scheduled 상태인지 아는 에서드
        '''
        from app import logger
        logger.info("BES: "+ str(Room.query.all()[1].status))
        room_query = Room.query.filter_by(user_id=self.id).filter_by(club_id=club.id)
        logger.info(room_query.filter(Room.status==RoomType.S.name).first())
        return room_query.filter(Room.status==RoomType.S.name).first()

    def is_resulted(self, club):
        '''
        내 방이 resulted 상태인지 아는 에서드
        '''
        room_query = Room.query.filter_by(user_id=self.id).filter_by(club_id=club.id)        
        return room_query.filter(Room.status==RoomType.R.name).first()

    def is_common(self, club):
        '''
        내 방이 common 혹은 notified 상태인지 아는 메서드
        '''
        room_query = Room.query.filter_by(user_id=self.id).filter_by(club_id=club.id)        
        if club.is_recruiting():
            return room_query.filter(Room.status!=RoomType.N.name).first() 
        return room_query.filter(Room.status!=RoomType.C.name).first()

    def select_rooms(self):
        rs = self.rooms.all()
        rooms = []
        for r in rs:
            if r.chats.offset(r.u_offset).count() != 0:
                rooms.append(r)
                
        return rooms

    def is_club_member(self, club):
        '''
        내가 해당 동아리의 맴버인지 아는 메서드
        '''
        return self.club_members.filter_by(club_id=club.id).first()
    
    def is_room_member(self, room):
        '''
        내가 해당 채팅방의 맴버인지 아는 메서드
        '''
        if room.user == self:
            return True
        if self.is_clubhead(room.club):
            return True
        return room.user_id == self.id

    def is_in_room(self, room):
        if room.id in rooms(sid=self.desktop_session_id, namespace='/chat'):
            return True
        if room.id in rooms(sid=self.mobile_session_id, namespace='/chat'):
            return True
        return False

    def __repr__(self):
        return '<User> {},{}'.format(self.name, self.gcn)
