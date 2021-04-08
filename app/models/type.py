import enum

# 채팅을 보내는 유저 타입
class UserType(enum.Enum):
    U = 1  # 유저
    C = 2  # 동아리장
    H1 = 3 # 동아리 지원
    H2 = 4 # 면접 일정
    H3 = 5 # 면접 결과
    H4 = 6 # 면접 응답

# 채팅방 상태
class RoomType(enum.Enum):
    C = 1 # 일반 채팅방
    N = 2 # 동아리 지원
    A = 3 # 지원자 채팅방
    S = 4 # 면접 일정을 받은 채팅방
    R = 5 # 면접 결과를 받은 채팅방


#fcm 송신자 타입
class FcmType(enum.Enum):
    C = 1 # 일반 채팅 메시지
    H = 2 # 봇이 보낸 메시지