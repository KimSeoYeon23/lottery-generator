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

    if not tickets:
        return JsonResponse({'error': '번호를 선택하세요.'}, status=400)

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
