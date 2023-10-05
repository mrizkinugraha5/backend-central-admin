from app_name.utilities import *
from app_name.helpers.function import *

# Kumpulan fungsi untuk memvalidasi body request
def regist_validator(nama,email,password):
    error_list =[]
    #validasi format nama
    validName = validateName(nama)
    if not validName:
        error_list.append("nama hanya boleh mengandung alphabet dan spasi")

    # Validasi format email
    validEmail = validateEmail(email)
    if not validEmail:
        error_list.append(f"format email tidak valid")

    # validasi password 
    invalid_password_list = validatepassword(password)
    if len(invalid_password_list) > 0:
        error_list += invalid_password_list

    return error_list


def account_validator(nama,email,password,nomor_telepon,is_pengusaha, nama_usaha, bidang_usaha, alamat_usaha):
    
    error_list =[]

    regist_error = regist_validator(nama,email,password)

    for i in regist_error:
        error_list.append(i)
        
    if nomor_telepon and not validatePhone(nomor_telepon):
        error_list.append(f"format nomor telepon tidak valid")
    
    if not str(is_pengusaha).isnumeric():
        error_list.append(f"is_pengusaha harus bertipe boolean")
    else:
        if int(is_pengusaha) not in [0, 1]:
            error_list.append(f"is_pengusaha harus bertipe boolean")

    for data in [nama_usaha, bidang_usaha, alamat_usaha]:
        if data != None:
            if not sanitize(data):
                error_list.append(f"{data} {INVALID_CHARACTER_INPUT}")

    return error_list 

def login_validator(email,password):
    error_list =[]
 
    # Validasi format email
    validEmail = validateEmail(email)
    if not validEmail:
        error_list.append(f"format email tidak valid")

    # validasi password 
    if not sanitize(password):
        error_list.append(f"password {INVALID_CHARACTER_INPUT}")
        

    return error_list 

def profile_validator(nama,jenis_kelamin, nomor_telepon,instagram,linkedin,is_pengusaha, nama_usaha, bidang_usaha, alamat, riwayat_kerja, tanggal_lahir, alamat_usaha):
    error_list = []
    # validasi nama 
    validName = validateName(nama)
    if not validName:
        error_list.append(f"nama hanya boleh mengandung alphabet dan spasi")

    # validasi jenis_kelamin
    if jenis_kelamin and jenis_kelamin not in ["laki-laki","perempuan"]:
        error_list.append(f"jenis kelamin tidak valid")

    #validasi nomor telpon
    if nomor_telepon and not validatePhone(nomor_telepon):
        error_list.append(f"format nomor telepon tidak valid")

    #validasi url
    if instagram and not url_validator(instagram):
        error_list.append(f"format url instagram tidak valid")

    if linkedin and not url_validator(linkedin):
        error_list.append(f"format url linkedin tidak valid")

    if type(is_pengusaha) != bool:
        error_list.append(f"is_pengusaha harus bertipe boolean")

    if not sanitize(nama_usaha):
        error_list.append(f"nama_usaha {INVALID_CHARACTER_INPUT}")

    if not sanitize(bidang_usaha):
        error_list.append(f"bidang_usaha {INVALID_CHARACTER_INPUT}")

    if not sanitize(alamat_usaha):
        error_list.append(f"alamat_usaha {INVALID_CHARACTER_INPUT}")

    if not sanitize(alamat):
        error_list.append(f"alamat {INVALID_CHARACTER_INPUT}")

    if not sanitize(riwayat_kerja):
        error_list.append(f"riwayat_kerja {INVALID_CHARACTER_INPUT}")

    if not is_date(tanggal_lahir):
        error_list.append(f"tanggal lahir tidak valid")

    return error_list


def update_password_validator(password_baru,confirm_password,password_lama,password_tersimpan):
    error_list = []
    if password_baru != confirm_password:
           error_list.append("password dan confirm password tidak sama")
    else:
        #cek apakah password lama sama dengan password yang tersimpan di database
        validPassword = checkPassword(password_tersimpan,password_lama)
        if not validPassword:      
               error_list.append("password lama salah")
                
        #cek apakah password baru sesuai format yang ditetapkan
        invalid_format_password_list = validatepassword(password_baru)
        if len(invalid_format_password_list) > 0:
            error_list += invalid_format_password_list 
            
    return error_list

def portofolio_validator(judul,deskripsi_singkat,deskripsi_lengkap):
    error_list = []
    if judul == "":
        error_list.append(f"judul tidak boleh kosong")
    if deskripsi_singkat == "":
        error_list.append(f"deskripsi_singkat tidak boleh kosong")
    if deskripsi_lengkap == "":
        error_list.append(f"deskripsi_lengkap tidak boleh kosong")

    return error_list

def event_validator(nama,nama_pemateri,nama_pemateri_2,link_conference,tanggal,waktu_mulai,waktu_berakhir,email,email_2,deskripsi,password,contact_whatsapp=None):
    error_list = []
    if nama == "":
        error_list.append(f"nama tidak boleh kosong")   
    if not sanitize_deskripsi(nama):
        error_list.append(f"nama {INVALID_DESKRIPSI}")
    if not validateName(nama_pemateri):
        error_list.append("nama_pemateri hanya boleh mengandung alphabet dan spasi")
    if nama_pemateri_2 != None and not validateName(nama_pemateri_2):
        error_list.append("nama_pemateri_2 hanya boleh mengandung alphabet dan spasi")
    if link_conference == "" or not url_validator(link_conference):
        error_list.append("format url conference tidak valid")
    if "tampil" not in link_conference:
        error_list.append("webinar hanya boleh dilaksanakan melalui platform tampil.id")
    if validateWhatsappContact(contact_whatsapp):
        error_list.append("format penulisan kontak whatsapp tidak valid")
    if not is_date(tanggal):
        error_list.append(f"tanggal tidak valid")
    if not validateEmail(email):
        error_list.append(f"format email tidak valid")
    if email_2 != None and not validateEmail(email_2):
        error_list.append(f"format email_2 tidak valid")
    if not sanitize_deskripsi(deskripsi):
        error_list.append(f"deskripsi {INVALID_DESKRIPSI}")
    if not is_datetime(waktu_mulai):
        error_list.append(f"waktu_mulai tidak valid")
    if not is_datetime(waktu_berakhir):
        error_list.append(f"waktu_berakhir tidak valid")
    if password != None and password == "":
        error_list.append(f"password tidak boleh kosong")   
    if password != None and not sanitize(password):
        error_list.append(f"password {INVALID_CHARACTER_INPUT}")
        
    return error_list

def kehadiran_validator(nama,email, nomor_telepon, sumber_info, is_pengusaha, nama_usaha, bidang_usaha,alamat_usaha):
    error_list =[]
    #validasi format nama
    validName = validateName(nama)
    if not validName:
        error_list.append("nama hanya boleh mengandung alphabet dan spasi")

    # Validasi format email
    validEmail = validateEmail(email)
    if not validEmail:
        error_list.append(f"format email tidak valid")

    if sumber_info not in ["centralai.id", "tampil.id"]:  
        error_list.append(f"sumber_info {sumber_info} tidak valid")

    if nomor_telepon and not validatePhone(nomor_telepon):
        error_list.append(f"format nomor telepon tidak valid")

    if not str(is_pengusaha).isnumeric():
        error_list.append(f"is_pengusaha harus bertipe boolean")
    else:
        if int(is_pengusaha) not in [0, 1]:
            error_list.append(f"is_pengusaha harus bertipe boolean")

    for data in [nama_usaha, bidang_usaha, alamat_usaha]:
        if data != None:
            if not sanitize(data):
                error_list.append(f"{data} {INVALID_CHARACTER_INPUT}")

    return error_list 

def link_validator(link,custom_name):
    error_list =[]
    if not validateName(custom_name):
        error_list.append("custom_name hanya boleh mengandung alphabet dan spasi")
    
    if link and not url_validator(link):
        error_list.append(f"format url tidak valid")

    return error_list


