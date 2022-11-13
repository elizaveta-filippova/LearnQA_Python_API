import json


def parse_json(json_text, key):
    obj = json.loads(json_text)
    if key in obj:
        return obj[key]


json_text = '''
{
  "messages": [
    {
      "message": "This is the first message",
      "timestamp": "2021-0-04 16:40:53"
    },
    {
      "message": "And this is a second message",
      "timestamp": "2021-06-04 16:41:01"
    }
  ]
}
'''
key = "messages"
inner_key = "message"

objects = parse_json(json_text=json_text, key=key)
if objects:
    second_object = objects[1]
    if inner_key in second_object:
        print(second_object[inner_key])
    else:
        print(f"Ключа {inner_key} нет в объекте JSON")
else:
    print(f"Ключа {key} нет в JSON")
