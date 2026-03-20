import json
import os
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from generator import LottoGenerator, PensionGenerator, get_stats
import client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def index(request):
    return FileResponse(open(os.path.join(BASE_DIR, 'static', 'index.html'), 'rb'), content_type='text/html')


@csrf_exempt
def api_buy_pension(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    body = json.loads(request.body) if request.body else {}
    groups   = body.get('groups', [])   # [1, 3, 5] 형태
    group    = body.get('group')
    if group and not groups:
        groups = [group]
    username = body.get('username', '')
    password = body.get('password', '')
    mock     = body.get('mock', False)

    if not groups:
        return JsonResponse({'error': '조(group)를 선택하세요.'}, status=400)

    if mock:
        import datetime
        today = datetime.date.today()
        base = datetime.date(2024, 12, 26)
        days = (3 - today.weekday()) % 7
        next_thu = today + datetime.timedelta(days=days)
        rnd = 244 + (next_thu - base).days // 7 - 1
        results = [{'round': rnd, 'group': g, 'numbers': [], 'mock': True} for g in groups]
        return JsonResponse({'results': results})

    if not username or not password:
        creds = client.load_credentials()
        if not creds:
            return JsonResponse({'error': '계정 정보가 없습니다.'}, status=401)
        username, password = creds['username'], creds['password']

    try:
        c = client.DhlotteryClient(username, password)
        results = []
        for g in groups:
            results.append(c.buy_pension(g))
        return JsonResponse({'results': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_pension_test(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)
    body = json.loads(request.body) if request.body else {}
    username = body.get('username', '')
    password = body.get('password', '')
    if not username or not password:
        creds = client.load_credentials()
        if not creds:
            return JsonResponse({'error': '계정 정보가 없습니다.'}, status=401)
        username, password = creds['username'], creds['password']
    try:
        c = client.DhlotteryClient(username, password)
        result = c.test_pension_format()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def api_stats(request):
    return JsonResponse(get_stats())


@csrf_exempt
def api_generate(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    body = json.loads(request.body) if request.body else {}
    lotto_count = body.get('lotto_count', 5)
    pension_count = body.get('pension_count', 5)

    lotto = LottoGenerator().generate(lotto_count)
    pension = PensionGenerator().generate(pension_count)
    stats = get_stats()

    return JsonResponse({'lotto': lotto, 'pension': pension, 'stats': stats})


@csrf_exempt
def api_balance(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    body = json.loads(request.body) if request.body else {}
    username = body.get('username', '')
    password = body.get('password', '')

    if not username or not password:
        creds = client.load_credentials()
        if not creds:
            return JsonResponse({'error': '계정 정보가 없습니다.'}, status=401)
        username = creds['username']
        password = creds['password']

    try:
        c = client.DhlotteryClient(username, password)
        result = c.get_balance()
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_buy(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    body = json.loads(request.body) if request.body else {}
    tickets = body.get('tickets', [])
    username = body.get('username', '')
    password = body.get('password', '')
    mock = body.get('mock', False)

    if not tickets:
        return JsonResponse({'error': '번호를 선택하세요.'}, status=400)

    if mock:
        import datetime
        today = datetime.date.today()
        draw = today + datetime.timedelta(days=(5 - today.weekday()) % 7)
        first = datetime.date(2002, 12, 7)
        rnd = 1 + (draw - first).days // 7
        bought = [
            {'slot': 'ABCDE'[i], 'mode': '수동', 'numbers': [str(n) for n in t]}
            for i, t in enumerate(tickets[:5])
        ]
        return JsonResponse({'round': rnd, 'draw_date': str(draw), 'tickets': bought, 'mock': True})

    if not username or not password:
        creds = client.load_credentials()
        if not creds:
            return JsonResponse({'error': '계정 정보가 없습니다.'}, status=401)
        username = creds['username']
        password = creds['password']

    try:
        c = client.DhlotteryClient(username, password)
        result = c.buy_lotto(tickets)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_save_credentials(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    body = json.loads(request.body) if request.body else {}
    username = body.get('username', '')
    password = body.get('password', '')

    if not username or not password:
        return JsonResponse({'error': '아이디와 비밀번호를 입력하세요.'}, status=400)

    client.save_credentials(username, password)
    return JsonResponse({'ok': True})
