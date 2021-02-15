from . import api_v1_0 as api

@api.route('/chat/{room_id}/chathelper/field', methods=['POST'])
def chathelper_field(room_id):
    pass

@api.route('/chat/{room_id}/chathelper/recruitment', methods=['POST'])
def chathelper_recruitment(room_id):
    pass

@api.route('/chat/{room_id}/chathelper/result', methods=['POST'])
def chathelper_result(room_id):
    pass

@api.route('/chat/{room_id}/chathelper/answer', methods=['POST'])
def chathelper_answer(room_id):
    pass
