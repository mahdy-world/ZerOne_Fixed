import os
import sys
import warnings
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# تجاهل التحذيرات
warnings.filterwarnings("ignore")

# إعداد المسارات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db/db.sqlite3')  # عدّله إذا تغير الاسم

# Folder ID الخاص بمجلد Google Drive الذي سترفع النسخ إليه
FOLDER_ID = '1suXDlvzuv53MqBHdTlws1vzWnQ5fzNlz'  # ← عدّله بحسب المجلد الذي أنشأته

# إعداد Google OAuth
gauth = GoogleAuth()
gauth.LoadCredentialsFile(os.path.join(BASE_DIR, "mycreds.txt"))

try:
    if gauth.credentials is None:
        gauth.LoadClientConfigFile(os.path.join(BASE_DIR, "credentials.json"))
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile(os.path.join(BASE_DIR, "mycreds.txt"))

    # إنشاء النسخة الاحتياطية داخل مجلد محدد
    drive = GoogleDrive(gauth)
    filename = f"db_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.sqlite3"

    file_drive = drive.CreateFile({
        'title': filename,
        'parents': [{'id': FOLDER_ID}]
    })
    file_drive.SetContentFile(DB_PATH)
    file_drive.Upload()

    print(f"تم رفع النسخة الاحتياطية إلى مجلد Google Drive: {filename}")
    sys.exit(0)

except Exception as e:
    print(f"فشل النسخ الاحتياطي: {e}")
    sys.exit(1)
