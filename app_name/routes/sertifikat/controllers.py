from wsgiref.util import request_uri
from flask import Blueprint, request, render_template, url_for
from flask_jwt_extended import  get_jwt, jwt_required
from werkzeug.utils import secure_filename
from flask import current_app as app
from time import strftime
from ...dbFunctions import Database
from ...utilities import *
from ...queries import *
from app_name.helpers.validator import *
from app_name.helpers.function import *
import threading
from PyPDF2 import PdfFileWriter, PdfFileReader
import io, math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import simpleSplit
from reportlab.lib.colors import HexColor
from PIL import Image
import PIL
from datetime import datetime

sertifikat = Blueprint(
    name='sertifikat',
    import_name=__name__,  
    static_folder = '../../static/pdf/sertifikat', 
    static_url_path="/media",
    url_prefix='/sertifikat'
)

@sertifikat.get('id/<id>')
@jwt_required()
def send_sertifikat_by_id_kehadiran(id):
    currentUser_role = get_jwt()["role"]
    url_list = request.url.split('/')[:-2]
    url = ('/').join(url_list)
    base_url_sertifikat = f'{url}/media'
    url_create = f'{url}/create'
    url_send = f'{url}/send/peserta'
    try:
        if currentUser_role != "ADMIN":
            return defined_error("hanya ADMIN yang dapat mengirimkan sertifikat","Forbidden",403)  
        # Ambil id_user dari jwt
        query = QUERY_GET_KEHADIRAN_BY_ID
        values = (id,)
        result = Database().get_data(query,values)

        if len(result) == 0:
            return defined_error(f"Kehadiran dengan id:{id} tidak ditemukan",'Not Found', 404)

        email_peserta = result[0]["email_peserta"]
        id_event = result[0]["id_event"]
        nama_event = result[0]["nama_event"]
        jenis_event = result[0]["jenis_event"]
        tanggal_event = result[0]["tanggal_event"].strftime("%d-%m-%Y")
        kode_kehadiran = result[0]["kode_kehadiran"]
        nama= result[0]["nama_peserta"]
        saved_url_sertifikat = result[0]["link_sertifikat"]

        template_email=None
        if saved_url_sertifikat:
            template_email = render_template(
                template_name_or_list="template_email.html",
                data={
                    "showGambar" : True,
                    "gambarURL" : app.config["BASE_URL"] + "/" + url_for("static", filename="icons/login.png"),
                    "judul" : "SERTIFIKAT KEHADIRAN PESERTA",
                    "deskripsi" : f"""
                    Terima kasih telah Berpartisipasi pada event ini.
                    sertifikat dapat diunduh pada : {saved_url_sertifikat}
                    """,
                }
            )
 
        def send_email_sertifikat():
                send_email(
                    penerima=email_peserta, 
                    judul="SERTIFIKAT KEHADIRAN PESERTA", 
                    template=template_email
                )
        def create_and_send():
            qr_code = instant_QR(id_event,email_peserta)
            sertifikat = get_sertifikat(nama, nama_event, kode_kehadiran,"peserta", jenis_event, qr_code, tanggal_event, url_create)
            url_sertifikat = sertifikat.json()['data'].split('/')[-1]
            url_sertifikat = f"{base_url_sertifikat}/{url_sertifikat}"
            save_sertifikat(url_sertifikat,kode_kehadiran)
            send_sertifikat(email_peserta,url_sertifikat,url_send)

        
        thread = threading.Thread(target=send_email_sertifikat) if saved_url_sertifikat else threading.Thread(target=create_and_send)
        thread.start()

        return success_data(message="Berhasil", data=f"mengirimkan sertifikat ke email:{email_peserta}")

    except Exception as e:
        return bad_request(str(e))

@sertifikat.get('/send/event/<kode>')
@jwt_required()
def send_email_by_event(kode):
    currentUser_role = get_jwt()["role"]
    url_list = request.url.split('/')[:-3]  
    url = ('/').join(url_list)
    url_peserta = f"{url}/id"
    url_narasumber = f"{url}/event/{kode}"
    try:
        if currentUser_role != "ADMIN":
            return defined_error("hanya ADMIN yang dapat mengirimkan sertifikat","Forbidden",403) 

        query = QUERY_GET_ALL_KEHADIRAN_BY_EVENT_KODE
        values = (kode,)
        result = Database().get_data(query,values)
        if len(result) == 0:
            return defined_error(f"event dengan kode:{kode} tidak ditemukan",'Not Found', 404)

        token = request.headers['Authorization']  
        headers = { "Authorization" : token}
        sendNarasumber = requests.request (
                            method="GET",
                            url=url_narasumber,
                            headers=headers
                        )
        
        for obj in result:
            url = f"{url_peserta}/{obj['id']}"
            sendPeserta = requests.request (
                            method="GET",
                            url=url,
                            headers=headers
                        )  
                 

        if sendNarasumber.status_code == 200 :
            return success_data(message="Berhasil", data=f"mengirim sertifikat webinar kode:{kode}")

    except Exception as e:
        return bad_request(str(e)) 

@sertifikat.get('/event/<kode>')
@jwt_required()
def send_email_speaker(kode): 
    currentUser_role = get_jwt()["role"]
    url_list = request.url.split('/')[:-2]  
    url = ('/').join(url_list)
    url_create = f"{url}/create"
    url_send = f"{url}/send/narasumber"
    base_url_sertifikat = f"{url}/media"
    try:
        if currentUser_role != "ADMIN":
            return defined_error("hanya ADMIN yang dapat mengirimkan sertifikat","Forbidden",403)  

        query = QUERY_GET_EVENT_BY_KODE
        values = (kode,)
        result = Database().get_data(query,values)
    
        if len(result) == 0:
            return defined_error(f"event dengan kode:{kode} tidak ditemukan",'Not Found', 404)

        tanggal = result[0]["tanggal"].strftime("%d-%m-%Y")
        pemateri_1 = result[0]["nama_pemateri"]
        pemateri_2 = result[0]["nama_pemateri_2"]

        event = result[0]["nama"]
        jenis_event = result[0]["jenis"]

        email_pemateri_1 = result[0]["email"]

        kode_event = result[0]["kode"]

        payload_1 = {
            "nama":pemateri_1,
            "email":email_pemateri_1,
            "kode_event": kode_event
        } 
        qr_pemateri_1 = generate_qr_code(payload_1)
        kode_kehadiran_1 = uuid.uuid4().hex[:6]  

        def generate_sertifikat():
            sertifikat_1 = get_sertifikat(pemateri_1,event,kode_kehadiran_1,"narasumber",jenis_event,qr_pemateri_1,tanggal,url_create)
            url_sertifikat = sertifikat_1.json()['data'].split('/')[-1]
            url_sertifikat = f"{base_url_sertifikat}/{url_sertifikat}"
            save_sertifikat(url_sertifikat,kode_kehadiran_1)
            send_sertifikat(email_pemateri_1,url_sertifikat,url_send)

            if pemateri_2:
                email_pemateri_2 = result[0]["email_2"]
                payload_2 = {
                    "nama":pemateri_2,
                    "email":email_pemateri_2,
                    "kode_event": kode_event
                }

                qr_pemateri_2 = generate_qr_code(payload_2)
                kode_kehadiran_2 = uuid.uuid4().hex[:6]

                sertifikat_2 = get_sertifikat(pemateri_2,event,kode_kehadiran_2,"narasumber",jenis_event,qr_pemateri_2,tanggal,url_create)
                url_sertifikat = sertifikat_2.json()['data'].split('/')[-1]
                url_sertifikat = f"{base_url_sertifikat}/{url_sertifikat}"
                save_sertifikat(url_sertifikat,kode_kehadiran_2)
                send_sertifikat(email_pemateri_2,url_sertifikat,url_send)
            
        thread = threading.Thread(target=generate_sertifikat)
        thread.start()

        return success_data(message="Berhasil", data=f"mengirim sertifikat narasumber webinar {event}")

    except Exception as e:
        return bad_request(str(e))

@sertifikat.post('/send/<role>')
def send_email_sertifikat(role):
    if role not in ['peserta', 'narasumber']:
        return defined_error(f'role {role} not valid')
    
    try:
        dataInput = request.json
        email = dataInput["email"].strip().lower()
        url_sertifikat = dataInput["url_sertifikat"].strip()

        judul = "SERTIFIKAT KEHADIRAN PESERTA"
        deskripsi = f"Terima kasih telah Berpartisipasi pada event ini. sertifikat dapat diunduh pada : {url_sertifikat}"
        if role == "narasumber" :
            judul = "SERTIFIKAT PENGHARGAAN SEBAGAI PEMBICARA"
            deskripsi = f"Terima kasih telah Berpartisipasi pada event ini selaku pembicara. sebagai bentuk penghargaan dan bukti tertulis kamu mendapatkan sertifikat yang dapat diunduh pada link berikut ini {url_sertifikat}"
       
        template_email = render_template(
                template_name_or_list="template_email.html",
                data={
                    "showGambar" : True,
                    "gambarURL" : app.config["BASE_URL"] + "/" + url_for("static", filename="icons/login.png"),
                    "judul" : judul,
                    "deskripsi" : deskripsi,
                }
            )

        def send_email_sertifikat():
            send_email(
                penerima=email, 
                judul=judul, 
                template=template_email
            )
        
        thread = threading.Thread(target=send_email_sertifikat)
        thread.start()

        create_log(f"berhasil mengirim sertifikat ke email: {email}")

        return success_data(message="Berhasil", data=f"berhasil mengirim email ke:{email}")

    except Exception as e:
        return bad_request(str(e))

@sertifikat.route('/create', methods=['POST'])
def create_sertifikat():
    data = request.json
    namaPeserta = data.get('namaPeserta').title()
    namaEvent = data['namaEvent'].title()
    kodeHadir = data['kodeHadir'].lower()
    jenisEvent = data['jenisEvent'].lower()
    role = data['role'].lower()
    qr = data['qr']
    tanggal = data['tanggal']
    tanggal = f'Jakarta, {tanggal}'

    if role not in ['peserta', 'narasumber']:
        return defined_error(f'{role} not valid role')
    if jenisEvent not in ['softskill', 'hardskill', 'centralclass-pos', 'centralclass-ocr', 'centralclass-chatbot']:
        return defined_error(f'{jenisEvent} not valid jenisEvent')

    # Preprocessing
    # =============
    # jenisEvent = 'centralclass-ocr'
    # namaClass = 'ocr'
    # jenisEvent = 'centralclass'

    if '-' in jenisEvent:
        jenisEvent = jenisEvent.split('-')
        namaClass = jenisEvent[1]
        jenisEvent = jenisEvent[0]
    
    existing_pdf = None
    if role == 'peserta' and jenisEvent == 'centralclass':
        existing_pdf = PdfFileReader(open(app.config['TEMPLATE_SERTIFIKAT'] + f'{role}/central_{namaClass}.pdf', "rb"))
    else:
        existing_pdf = PdfFileReader(open(app.config['TEMPLATE_SERTIFIKAT'] + f'{role}/{jenisEvent}.pdf', "rb"))
    
    page = existing_pdf.pages[0]

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page.mediabox.width, page.mediabox.height))

    pdfmetrics.registerFont(TTFont('Bitter', app.config['FONTS']+'Bitter-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('Archivo', app.config['FONTS']+'Archivo-Bold.ttf'))

    if jenisEvent == "softskill":
        # nama peserta
        can.setFont("Bitter", 40)
        can.setFillColor(HexColor('#87AAAA'))
        namaPeserta = simpleSplit(namaPeserta, "Bitter", 40, 564)
        y_axis = 215
        for words in namaPeserta:
            can.drawString(150, y_axis+(len(namaPeserta)*54), words)
            y_axis-=40
        
        # nama event
        can.setFont("Archivo", 18)
        can.setFillColor(HexColor('#171717'))
        namaEvent = simpleSplit(namaEvent, "Archivo", 18, 429)
        y_axis = 210
        for words in namaEvent:
            can.drawString(152, y_axis, words)
            y_axis-= 18

        can.setFont("Archivo", 11)
        can.setFillColor(HexColor('#171717'))
        tanggal = simpleSplit(tanggal, "Archivo", 11, 429)
        y_axis = 160
        for words in tanggal:
            can.drawString(152, y_axis, words)
            y_axis-= 10

        # gambar qr
        img = PIL.Image.open(io.BytesIO(base64.b64decode(qr)))
        img = img.resize((120, 120))
        img.save(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg')
        can.drawImage(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg', 619, 130, width=115, preserveAspectRatio=True, mask='auto')
        can.save()
        os.remove(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg')
    
    elif jenisEvent == "hardskill":
        # nama peserta
        can.setFont("Bitter", 40)
        can.setFillColor(HexColor('#F4C06C'))
        namaPeserta = simpleSplit(namaPeserta, "Bitter", 40, 710)
        y_axis = 340
        for words in namaPeserta:
            w_namaPeserta = stringWidth(words,"Bitter", 40)
            can.drawString((float(page.mediabox.width)-w_namaPeserta)/2, y_axis, words)
            y_axis-=40
        
        # nama event
        can.setFont("Archivo", 18)
        can.setFillColor(HexColor('#E9EEF1'))
        namaEvent = simpleSplit(namaEvent, "Archivo", 18, 710)
        y_axis = 225
        for words in namaEvent:
            w_namaEvent = stringWidth(words,"Bitter", 18)
            can.drawString((float(page.mediabox.width)-w_namaEvent)/2, y_axis, words)
            y_axis-=20

        # tanggal event
        can.setFont("Archivo", 12)
        can.setFillColor(HexColor('#E9EEF1'))
        tanggal = simpleSplit(tanggal, "Archivo", 12, 710)
        y_axis = 170
        for words in tanggal:
            w_tanggal = stringWidth(words,"Bitter", 12)
            can.drawString((float(page.mediabox.width)-w_tanggal)/2, y_axis, words)
            y_axis-= 8
        
        # gambar qr
        img = PIL.Image.open(io.BytesIO(base64.b64decode(qr)))
        img = img.resize((120, 120))
        img.save(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg')
        can.drawImage(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg', 651, 65, width=115, preserveAspectRatio=True, mask='auto')
        can.save()
        os.remove(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg')

    elif jenisEvent == "centralclass" and role == 'narasumber':
        # nama peserta
        can.setFont("Bitter", 40)
        can.setFillColor(HexColor('#000000'))
        namaPeserta = simpleSplit(namaPeserta, "Bitter", 40, 710)
        y_axis = 270
        for words in namaPeserta:
            w_namaPeserta = stringWidth(words,"Bitter", 40)
            can.drawString(75, y_axis+(len(namaPeserta)*20), words)
            y_axis-=40
        
        # nama event
        can.setFont("Archivo", 18)
        can.setFillColor(HexColor('#00000'))
        namaEvent = simpleSplit(namaEvent, "Archivo", 18, 710)
        y_axis = 205
        for words in namaEvent:
            w_namaEvent = stringWidth(words,"Bitter", 18)
            can.drawString(72, y_axis, words)
            y_axis-=10

        # nama event
        can.setFont("Archivo", 12)
        can.setFillColor(HexColor('#00000'))
        tanggal = simpleSplit(tanggal, "Archivo", 12, 710)
        y_axis = 180
        for words in tanggal:
            w_tanggal = stringWidth(words,"Bitter", 12)
            can.drawString(72, y_axis, words)
            y_axis-= 8
        
        # gambar qr
        img = PIL.Image.open(io.BytesIO(base64.b64decode(qr)))
        img = img.resize((120, 120))
        img.save(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg')
        can.drawImage(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg', 651, 65, width=115, preserveAspectRatio=True, mask='auto')
        can.save()
        os.remove(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg')

    elif jenisEvent == "centralclass":
        # nama peserta
        can.setFont("Bitter", 30)
        can.setFillColor(HexColor('#000000'))
        namaPeserta = simpleSplit(namaPeserta, "Bitter", 30, 564)
        y_axis = 250
        for words in namaPeserta:
            can.drawString(65, y_axis+(len(namaPeserta)*54), words)
            y_axis-=30
        
        # nama event
        can.setFont("Archivo", 18)
        can.setFillColor(HexColor('#000000'))
        namaEvent = simpleSplit(namaEvent, "Archivo", 18, 429)
        y_axis = 250
        for words in namaEvent:
            can.drawString(66, y_axis, words)
            y_axis-=19
        
        # nama peserta
        can.setFont("Archivo",12)
        can.setFillColor(HexColor('#000000'))
        tanggal = simpleSplit(tanggal, "Archivo",12, 429)
        y_axis = 210
        for words in tanggal:
            can.drawString(66, y_axis, words)
            y_axis-=18

        # gambar qr
        img = PIL.Image.open(io.BytesIO(base64.b64decode(qr)))
        img = img.resize((120, 120))
        img.save(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg')
        can.drawImage(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg', 680, 50, width=115, preserveAspectRatio=True, mask='auto')
        can.save()
        os.remove(app.config['SERTIFIKAT'] + f'{kodeHadir}.jpeg')
    
    new_pdf = PdfFileReader(packet)
    output = PdfFileWriter()
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    outputStream = open(app.config['SERTIFIKAT'] + f'{kodeHadir}.pdf', "wb")
    output.write(outputStream)
    outputStream.close()

    return success_data("Berhasil membuat sertifikat", app.config['SERTIFIKAT'] + f'{kodeHadir}.pdf')


@sertifikat.post('/verifikasi')
@jwt_required()
def cek_sertifikat():
    currentUser_role = get_jwt()["role"]
    try:
        if currentUser_role != "ADMIN":
            return defined_error("hanya ADMIN yang dapat mengirimkan sertifikat","Forbidden",403)  
        dataInput = request.json
        dataRequired = ["kode_event", "nama","email"]
        for data in dataRequired:
            if dataInput == None:
                return bad_request("body request tidak boleh kosong")
            if data not in dataInput:
                return parameter_error(f"Missing {data} in Request Body")
            if dataInput[data] == None:
                dataInput[data] = ""

        kode_event = dataInput["kode_event"].strip()
        nama = dataInput["nama"].strip()
        email = dataInput["email"].strip().lower()

        query = QUERY_CHECK_KEHADIRAN
        values = (kode_event,nama,email,)
        result = Database().get_data(query, values)
        if len(result) == 0:
            return success_data(message=f"Success", data={'status':'invalid'})
        else:
            return success_data(message=f"Success", data={'status':'valid'})


    except Exception as e:
        return bad_request(str(e))