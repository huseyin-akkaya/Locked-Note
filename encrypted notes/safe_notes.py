from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
from cryptography.fernet import Fernet
import hashlib
import os
import json


#key dosyası oluşturma fonksiyonu
def load_or_create_key():
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as f:
            f.write(key)
        return key
#sabit keyi alır
SECRET_KEY = load_or_create_key()
fernet = Fernet(SECRET_KEY)#şifre ve deşifre için

#şifreyi hashleme
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

#not kaydetme fonksiyonu
def save_note():
    title = title_entry.get()#başlığı al
    note = input_secret.get("1.0", END).strip()#not içeriğini al
    password = entry_password.get()#şifreyi al

    # Alanlardan biri boşsa hata göster
    if not title or not note or not password:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    #Notu şifrele
    encrypted_note = fernet.encrypt(note.encode()).decode()
    # Şifreyi hashle
    password_hash = hash_password(password)

    #dosyaya veriyi işleme
    data = {
        "password_hash": password_hash,
        "note": encrypted_note
    }

    with open(f"{title}.json", "w") as f:
        json.dump(data, f)

    #kayıt mesajı
    messagebox.showinfo("Successful", "The note was saved!")
    #alanı temizle
    title_entry.delete(0, END)
    input_secret.delete("1.0", END)
    entry_password.delete(0, END)

    #notu açma ve deşifreleme fonksiyonu
def open_note():
    title = title_entry.get()
    password = entry_password.get()

    # Alanlardan biri boşsa hata göster
    if not title or not password:
        messagebox.showerror("Error", "Enter the title and password.")
        return

    # Dosya yoksa hata göster
    if not os.path.exists(f"{title}.json"):
        messagebox.showerror("Error", "No such note was found.")
        return

    # dosyayı oku
    with open(f"{title}.json", "r") as f:
        data = json.load(f)

    password_hash = hash_password(password)# Girilen şifreyi hashle

    #hash kontrolü ile şifrenin doğruluğu yanlışlığına bakılır
    if data["password_hash"] != password_hash:
        messagebox.showerror("Error", "The wrong password!")
        return

    # Şifre doğruysa notu çöz
    decrypted_note = fernet.decrypt(data["note"].encode()).decode()
    input_secret.delete("1.0", END)
    input_secret.insert(END, decrypted_note)

#ekranın oluşturulması
window = Tk()
window.title("Encrypted Notes")
window.config(padx=20, pady=20)

#ekranın üstüne konumlandırılacak resimin boyutlandırılması
image = Image.open("lock_picture.png")
resized = image.resize((150, 80))
img = ImageTk.PhotoImage(image=resized)

#resimi açılan pencereye ekleme
label = Label(window, image = img)
label.image = img
label.pack()

#tittle girişi
enter_title = Label(window, text="Enter your title", font=("Arial black", 9))
enter_title.pack(pady=10)

title_entry = Entry(window)
title_entry.pack()

#not girişi
enter_secret = Label(window,text="Enter your secret", font=('Arial black',10) )
enter_secret.pack(pady=10)

input_secret =  Text(window, width=40, height=10, font=('Arial', 10))
input_secret.pack()

enter_secret = Label(window,text="Enter master key", font=('Arial black',10) )
enter_secret.pack(pady=10)

#key girişi
entry_password = Entry(window, show="*")
entry_password.pack()

#kayıt etme butonu
click = Button(window,text="Save & Encrypt",command=save_note)
click.pack(pady=10)

#kayıtlı dosyayı açma butonu
click = Button(text="Decrypt",command=open_note)
click.pack()

window.mainloop()
