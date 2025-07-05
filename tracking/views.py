from django.shortcuts import render
import requests

DAFTAR_KURIR_BINDERBYTE = [
    {'nama': 'JNE Express', 'kode': 'jne'},
    {'nama': 'POS Indonesia', 'kode': 'pos'},
    {'nama': 'J&T Express', 'kode': 'jnt'},
    {'nama': 'SiCepat Ekspres', 'kode': 'sicepat'},
    {'nama': 'TIKI', 'kode': 'tiki'},
    {'nama': 'Anteraja', 'kode': 'anteraja'},
    {'nama': 'Wahana Express', 'kode': 'wahana'},
    {'nama': 'Ninja Xpress', 'kode': 'ninja'},
    {'nama': 'Lion Parcel', 'kode': 'lion'},
    {'nama': 'Shopee Express', 'kode': 'spx'},
    {'nama': 'ID Express', 'kode': 'ide'},
]

def index(request):
    return render(request, 'tracking/index.html', {'daftar_kurir': DAFTAR_KURIR_BINDERBYTE})

def hasil(request):
    hasil_tracking = None
    error_message = None

    if request.method == 'POST':
        no_resi = request.POST.get('no_resi')
        kurir = request.POST.get('kurir')
        api_key = '42a458c5a036048360db16c653c4d78c1d3ea524ff661c3c6903819f72b1f395'

        if not no_resi or not kurir:
            error_message = "Nomor resi dan kurir tidak boleh kosong."
            return render(request, 'tracking/hasil.html', {'data': None, 'error': error_message})

        try:
            response = requests.get(
                "https://api.binderbyte.com/v1/track",
                params={"api_key": api_key, "courier": kurir, "awb": no_resi},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            if result.get('status') == 200 and 'data' in result:
                summary = result['data'].get('summary', {})
                history = result['data'].get('history', [])

                formatted_history = []
                for item in history:
                    formatted_history.append({
                        'status': item.get('desc', 'N/A'),
                        'lokasi': item.get('location', 'N/A'),
                        'waktu': item.get('date', 'N/A'),
                        'active': True if item == history[0] else False
                    })

                hasil_tracking = {
                    'no_resi': summary.get('awb', no_resi),
                    'kurir': next((k['nama'] for k in DAFTAR_KURIR_BINDERBYTE if k['kode'] == kurir), kurir.upper()),
                    'status': history[0].get('desc', 'Sedang diproses') if history else 'Sedang diproses',
                    'penerima': summary.get('receiver', 'N/A'),
                    'alamat': summary.get('destination', 'N/A'),
                    'estimasi': summary.get('estimation_date', 'N/A'),
                    'history': formatted_history,
                }
            else:
                error_message = result.get('message', 'Resi tidak ditemukan atau terjadi kesalahan.')

        except requests.exceptions.RequestException as e:
            error_message = f"Gagal terhubung ke API: {str(e)}"
        except Exception as e:
            error_message = "Terjadi kesalahan saat memproses data."
            print(f"Error: {str(e)}")

    return render(request, 'tracking/hasil.html', {
        'data': hasil_tracking,
        'error': error_message
    })
