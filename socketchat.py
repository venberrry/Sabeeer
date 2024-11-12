from flask_socketio import emit, Namespace
from transliterate import translit

class Chat(Namespace):
    def on_connect(self):
        print('Есть коннект к чату')

    def on_disconnect(self):
        print('Есть выход из чата')

    def on_send_msg(self, data: dict):
        print(f"Полчили сообщение: {data['msg']}")
        if data['msg']:
            length_msg = len(data['msg'])
            latin_msg = translit(data['msg'], "ru", reversed=True)
            new_dict = {
                'length_msg': length_msg,
                'latin_msg': latin_msg
            }
            emit('mymsg', data['msg'], broadcast=True, namespace='/chat')
            emit('recv', new_dict, broadcast=True, namespace='/chat')
