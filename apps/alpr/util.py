import json


def response(Response, msg, status=200):
    return Response(json.dumps({'status': status, 'msg': msg}), status=status, mimetype="application/json")


def save_to_json(json_obj_collection_all, filename):
    with open('apps/log/{}.json'.format(filename), 'w', encoding='utf-8') as f:
        json.dump(json_obj_collection_all, f, ensure_ascii=False, indent=4)
