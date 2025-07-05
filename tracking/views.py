from django.shortcuts import render
import requests
import json

# Daftar kurir
DAFTAR_KURIR_BINDERBYTE = [
    {'nama': 'PCP Express', 'kode': 'pcp'},
    {'nama': 'JET Express', 'kode': 'jet'},
    {'nama': 'REX Express', 'kode': 'rex'},
    {'nama': 'First Logistics', 'kode': 'first'},
    {'nama': 'ID Express', 'kode': 'ide'},
    {'nama': 'KGXpress', 'kode': 'kgx'},
    {'nama': 'SAP Express', 'kode': 'sap'},
    {'nama': 'JX Express', 'kode': 'jxe'},
    {'nama': 'RPX', 'kode': 'rpx'},
    {'nama': 'Lazada Express', 'kode': 'lex'},
    {'nama': 'Indah Cargo', 'kode': 'indah_cargo'},
    {'nama': 'Dakota Cargo', 'kode': 'dakota'},
    {'nama': 'Kurir Rekomendasi (Tokopedia)', 'kode': 'kurir_tokopedia'},
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
        url = "https://api.binderbyte.com/v1/track"
        params = {
            "api_key": api_key,
            "courier": kurir,
            "awb": no_resi
        }

        if not no_resi or not kurir:
            error_message = "Nomor resi dan pilihan kurir tidak boleh kosong."
            return render(request, 'tracking/hasil.html', {'data': None, 'error': error_message})

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get('status') == 200:
                if ('data' in result and 'summary' in result['data'] and
                        'history' in result['data'] and len(result['data']['history']) > 0):

                    detail = result['data']['summary']
                    history = result['data']['history']

                    hasil_tracking = {
                        'no_resi': detail.get('awb', 'N/A'),
                        'kurir': detail.get('courier', 'N/A'),
                        'status': history[0].get('desc', 'N/A'),
                        'lokasi': history[0].get('location', 'N/A'),
                        'waktu': history[0].get('date', 'N/A'),
                        'penerima': detail.get('receiver', 'N/A'),
                        'alamat': detail.get('address', 'N/A'),
                        'estimasi': detail.get('service', 'N/A'),
                        'history': history
                    }
                else:
                    error_message = "Data tracking tidak lengkap atau tidak ditemukan."
            else:
                error_message = result.get('message', 'Terjadi kesalahan pada API.')

        except requests.exceptions.HTTPError as errh:
            if response.status_code == 401:
                error_message = "API Key tidak valid. Periksa kembali."
            elif response.status_code == 403:
                error_message = "Akses ditolak. Mungkin kuota habis."
            elif response.status_code == 400:
                error_message = "Permintaan tidak valid. Cek nomor resi dan kurir."
            else:
                error_message = f"HTTP Error: {response.status_code}"
        except requests.exceptions.ConnectionError:
            error_message = "Tidak dapat terhubung ke server Binderbyte."
        except requests.exceptions.Timeout:
            error_message = "Permintaan ke API melebihi batas waktu."
        except requests.exceptions.RequestException as e:
            error_message = f"Kesalahan tak terduga: {e}"
        except json.JSONDecodeError:
            error_message = "Respon dari server tidak valid JSON."
        except KeyError:
            error_message = "Terjadi kesalahan saat membaca data."
        except IndexError:
            error_message = "Riwayat pengiriman tidak tersedia."
        except Exception as e:
            error_message = f"Kesalahan internal: {e}"

    return render(request, 'tracking/hasil.html', {
        'data': hasil_tracking,
        'error': error_message
    })
