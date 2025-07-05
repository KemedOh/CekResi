from django.shortcuts import render
import requests
import json

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
    # Tambahkan lainnya bila perlu
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

                hasil_tracking = {
                    'no_resi': summary.get('awb', 'N/A'),
                    'kurir': summary.get('courier', 'N/A'),
                    'status': history[0].get('desc', 'N/A') if history else 'N/A',
                    'lokasi': history[0].get('location', 'N/A') if history else 'N/A',
                    'waktu': history[0].get('date', 'N/A') if history else 'N/A',
                    'penerima': summary.get('receiver_name', 'N/A'),
                    'alamat': summary.get('receiver_address', 'N/A'),
                    'estimasi': summary.get('estimation', 'N/A'),
                    'history': history,
                }
            else:
                error_message = result.get('message', 'Resi tidak ditemukan.')

        except Exception as e:
            print("Error:", e)
            error_message = "Terjadi kesalahan saat memproses permintaan."

    return render(request, 'tracking/hasil.html', {
        'data': hasil_tracking,
        'error': error_message
    })
