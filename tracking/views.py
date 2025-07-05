from django.shortcuts import render
import requests
import json # Import modul json untuk penanganan error JSON

# --- Definisi Daftar Kurir ---
# Ini adalah daftar kurir yang akan dikirim ke template HTML
# Pastikan kode (value) sesuai dengan yang didukung Binderbyte (huruf kecil)
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
    # Tambahkan kurir umum lainnya yang Anda rangkum sebelumnya jika diperlukan
    {'nama': 'JNE Express', 'kode': 'jne'},
    {'nama': 'POS Indonesia', 'kode': 'pos'},
    {'nama': 'J&T Express', 'kode': 'jnt'},
    {'nama': 'SiCepat Ekspres', 'kode': 'sicepat'},
    {'nama': 'TIKI', 'kode': 'tiki'},
    {'nama': 'Anteraja', 'kode': 'anteraja'},
    {'nama': 'Wahana Express', 'kode': 'wahana'},
    {'nama': 'Ninja Xpress', 'kode': 'ninja'},
    {'nama': 'Lion Parcel', 'kode': 'lion'},
    {'nama': 'Shopee Express', 'kode': 'spx'}, # Menambahkan Shopee Express (spx)
]


def index(request):
    """
    Menampilkan halaman utama untuk input nomor resi dan pilihan kurir.
    Mengirimkan daftar kurir ke template.
    """
    return render(request, 'tracking/index.html', {'daftar_kurir': DAFTAR_KURIR_BINDERBYTE})


def hasil(request):
    """
    Memproses request POST untuk cek resi melalui API Binderbyte.
    Menangani berbagai skenario error dan menampilkan hasil atau pesan error.
    """
    hasil_tracking = None
    error_message = None

    if request.method == 'POST':
        no_resi = request.POST.get('no_resi')
        kurir = request.POST.get('kurir') # Mengambil kode kurir dari form

        # Ganti dengan API Key Binderbyte Anda yang sebenarnya dan aktif
        # Disarankan untuk menyimpan API Key di settings.py atau environment variable
        # Untuk tujuan contoh, kita letakkan di sini.
        api_key = '42a458c5a036048360db16c653c4d78c1d3ea524ff661c3c6903819f72b1f395' 
        
        # URL Endpoint API Binderbyte
        url = "https://api.binderbyte.com/v1/track"
        
        # Parameter yang akan dikirimkan ke API
        params = {
            "api_key": api_key,
            "courier": kurir,
            "awb": no_resi
        }

        if not no_resi or not kurir:
            error_message = "Nomor resi dan pilihan kurir tidak boleh kosong."
            return render(request, 'tracking/hasil.html', {'data': None, 'error': error_message})

        try:
            # Mengirim request GET ke API Binderbyte dengan timeout 10 detik
            response = requests.get(url, params=params, timeout=10) 
            
            # Ini akan memunculkan HTTPError untuk status code 4xx (Client Error) atau 5xx (Server Error)
            response.raise_for_status() 

            # Mengubah respons JSON menjadi dictionary Python
            result = response.json()
            
            # --- DEBUGGING AIDS (Aktifkan saat debugging, nonaktifkan saat production) ---
            print(f"API Request URL: {response.url}")
            print(f"API Response Status Code: {response.status_code}")
            print(f"API Raw Response: {response.text}")
            # --- END DEBUGGING AIDS ---

            # Memeriksa status dari respons Binderbyte itu sendiri (bukan HTTP status code)
            if result.get('status') == 200:
                # Memastikan kunci 'data', 'summary', dan 'history' ada sebelum diakses
                if ('data' in result and 'summary' in result['data'] and 
                    'history' in result['data'] and len(result['data']['history']) > 0):
                    
                    detail = result['data']['summary']
                    delivery_status = result['data']['history'][0] # Mengambil status terakhir

                    hasil_tracking = {
                        # Menggunakan .get() dengan nilai default 'N/A' untuk menghindari KeyError
                        'no_resi': detail.get('awb', 'N/A'),
                        'kurir': detail.get('courier', 'N/A'),
                        'status': delivery_status.get('desc', 'N/A'),
                        'lokasi': delivery_status.get('location', 'N/A'),
                        'waktu': delivery_status.get('date', 'N/A')
                    }
                else:
                    error_message = "Data tracking tidak lengkap atau tidak ditemukan. Mohon cek kembali nomor resi dan kurir."
            else:
                # Jika status dari Binderbyte bukan 200, ambil pesan errornya
                error_message = result.get('message', 'Resi tidak ditemukan atau terjadi kesalahan pada layanan Binderbyte.')

        except requests.exceptions.HTTPError as errh:
            # Menangani kesalahan HTTP (misal: 401 Unauthorized, 403 Forbidden, 404 Not Found)
            print(f"HTTP Error from Binderbyte: {errh}")
            print(f"Response content: {getattr(response, 'text', 'No response content')}") # Handle if response object itself is incomplete
            error_message = f"Terjadi kesalahan HTTP ({response.status_code}). Pesan: {response.text}"
            if response.status_code == 401:
                error_message = "API Key tidak valid atau tidak memiliki akses. Periksa API Key Binderbyte Anda."
            elif response.status_code == 403:
                error_message = "Akses ditolak. Kemungkinan kuota API Anda habis atau API Key tidak aktif."
            elif response.status_code == 400:
                error_message = "Permintaan tidak valid. Pastikan nomor resi dan kode kurir benar."
        except requests.exceptions.ConnectionError as errc:
            # Menangani masalah koneksi jaringan (misal: server Binderbyte tidak dapat dijangkau, DNS error, firewall)
            print(f"Connection Error: {errc}")
            error_message = "Tidak dapat terhubung ke server Binderbyte. Periksa koneksi internet Anda atau firewall."
        except requests.exceptions.Timeout as errt:
            # Menangani jika permintaan ke API melebihi batas waktu (timeout)
            print(f"Timeout Error: {errt}")
            error_message = "Permintaan ke Binderbyte melebihi batas waktu. Coba lagi nanti."
        except requests.exceptions.RequestException as err:
            # Menangani semua jenis kesalahan lain dari library requests
            print(f"An unexpected request error occurred: {err}")
            error_message = f"Terjadi kesalahan tak terduga saat menghubungi API: {err}"
        except json.JSONDecodeError:
            # Menangani jika respons dari API bukan format JSON yang valid
            print(f"JSON Decode Error: Response content was not valid JSON. Response: {getattr(response, 'text', 'No response content')}")
            error_message = "Respons dari server bukan format yang valid. Mohon hubungi administrator."
        except KeyError as ke:
            # Menangani jika struktur JSON respons tidak sesuai harapan (kunci tidak ditemukan)
            print(f"KeyError in JSON response: {ke}. Full response: {result}")
            error_message = f"Terjadi masalah dalam membaca data resi. Data tidak lengkap atau format berubah."
        except IndexError as ie:
            # Menangani jika list history kosong
            print(f"IndexError: {ie}. History list might be empty. Full response: {result}")
            error_message = "Riwayat pengiriman tidak ditemukan untuk resi ini."
        except Exception as e:
            # Catch-all untuk error lain yang tidak terduga
            print(f"An unknown error occurred: {e}")
            error_message = f"Terjadi kesalahan internal pada aplikasi: {e}"

    # Mengembalikan template hasil dengan data tracking atau pesan error
    return render(request, 'tracking/hasil.html', {'data': hasil_tracking, 'error': error_message})