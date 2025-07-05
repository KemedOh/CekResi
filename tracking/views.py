from django.shortcuts import render
import requests

def index(request):
    return render(request, 'tracking/index.html')  # Pastikan file HTML-nya ada

def hasil(request):
    if request.method == 'POST':
        no_resi = request.POST.get('no_resi')
        kurir = request.POST.get('kurir')

        api_key = '8e49f28e0f2f2cf56393c352613eec358e85fb7077ce6f7f453ebb826a7b1f6d'
        url = f"https://api.binderbyte.com/v1/track?api_key={api_key}&courier={kurir}&awb={no_resi}"

        response = requests.get(url)

        if response.status_code == 200:
            result = response.json()

            if result['status'] == 200:
                detail = result['data']['summary']
                delivery_status = result['data']['history'][0]  # status terakhir

                hasil_tracking = {
                    'no_resi': detail['awb'],
                    'kurir': detail['courier'],
                    'status': delivery_status['desc'],
                    'lokasi': delivery_status['location'],
                    'waktu': delivery_status['date']
                }

                return render(request, 'tracking/hasil.html', {'data': hasil_tracking})
            else:
                error = result.get('message', 'Resi tidak ditemukan.')
                return render(request, 'tracking/hasil.html', {'data': None, 'error': error})

        return render(request, 'tracking/hasil.html', {'data': None, 'error': 'Terjadi kesalahan saat menghubungi API.'})
