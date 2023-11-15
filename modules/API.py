import requests

class PostChatEntity:
  def __init__(self, robot_id, mode, message):
    self.robot_id = robot_id
    self.mode = mode
    self.message = message

class API:
  def __init__(self, api_endpoint):
    self.api_endpoint = api_endpoint

  def post_chat_message(self, payload: PostChatEntity):
    print("api server) post_chat_message")
    url = "{0}/test".format(self.api_endpoint)
    # print(payload.mode)
    data = {
        'MSG': payload.message,
        'MODE': 0,
        'ROBOT_ID': int(payload.robot_id)
    }

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, headers=headers, json=data)
    
    return response