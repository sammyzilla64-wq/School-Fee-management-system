import os
import sys

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
def leta_data():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="shule_fees_db",
            use_pure=True,
            charset="utf8",
            collation="utf8_general_ci"
        )
        cursor = conn.cursor()
        query = """
SELECT w.id, w.jina_kamili, d.jina_la_darasa, d.kiasi_cha_ada,
COALESCE(SUM(m.kiasi_kilicholipwa), 0),
(d.kiasi_cha_ada - COALESCE(SUM(m.kiasi_kilicholipwa), 0))
FROM mwanafunzi w
JOIN madarasa d ON w.darasa_id = d.id
LEFT JOIN malipo m ON w.id = m.mwanafunzi_id
GROUP BY w.id
"""

        cursor.execute(query)
        rows = cursor.fetchall()
        for row in tree.get_children():
            tree.delete(row)
        jumla_ada = 0
        jumla_pato = 0
        jumla_madeni = 0
        neno_tafuta = entry_tafuta.get().lower()

        for row in rows:
            mwanafunzi_jina = row[1].lower()

            if neno_tafuta and neno_tafuta not in mwanafunzi_jina:
               continue

            jumla_ada += float(row[3])
            jumla_pato += float(row[4])
            jumla_madeni += float(row[5])

            tag = "deni" if float(row[5]) > 0 else "safi"

            tree.insert("", tk.END, values=(
                row[0], row[1], row[2],
                f"{row[3]:,}", f"{row[4]:,}", f"{row[5]:,}"
            ), tags=(tag,))

        lbl_dash_ada.config(text=f"TZS {jumla_ada:,.0f}")
        lbl_dash_pato.config(text=f"TZS {jumla_pato:,.0f}")
        lbl_dash_deni.config(text=f"TZS {jumla_madeni:,.0f}")

        tree.update()

        conn.close()
    except Exception as e:
        messagebox.showerror("Kosa", f"Imeshindwa kuvuta data: {e}")

def weka_malipo():
    mwanafunzi_id_raw = entry_id.get()
    kiasi_raw = entry_kiasi.get()

    if not mwanafunzi_id_raw or not kiasi_raw:
        messagebox.showwarning("Onyo", "Jaza sehemu zote!")
        return
    try:
        mwanafunzi_id = int(mwanafunzi_id_raw)
        kiasi = float(kiasi_raw)
        
        conn = mysql.connector.connect(
           host="localhost",
           user="root",
           password="",
           database="shule_fees_db",
           use_pure=True,
           charset="utf8",
           collation="utf8_general_ci"
           
        )
        cursor = conn.cursor()

        sql = "INSERT INTO malipo (mwanafunzi_id, kiasi_kilicholipwa) VALUES (%s, %s)"
        cursor.execute(sql, (mwanafunzi_id, kiasi))
        
        conn.commit()
        cursor.close()
        conn.close()

        messagebox.showinfo("Mafanikio", "Malipo yamesajiliwa kikamilifu!")
        entry_id.delete(0, tk.END)
        entry_kiasi.delete(0, tk.END)
        leta_data()

    except Exception as e:
        messagebox.showerror("Kosa", f"imeshindwa kuweka malipo: {e}")

def toa_stakabadhi():
    import time
    import datetime
    
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Onyo", "Tafadhali chagua mwanafunzi kwenye jedwali kwanza!")
        return

    item_data = tree.item(selected_item)['values']
    m_id, jina, darasa, ada, aliyolipa, deni = item_data
    
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    pdf_name = os.path.join(desktop_path, f"Stakabadhi_{m_id}.pdf")

    namba_risiti = f"REC-{time.strftime('%Y%M%S')}-{m_id}"
    muda_saa = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    c = canvas.Canvas(pdf_name, pagesize=letter)

    c.saveState()
    c.setFont("Helvetica-Bold", 55)
    c.setFillColorRGB(0.96, 0.96, 0.96)
    c.translate(300, 500)
    c.rotate(35)
    c.drawCentredString(0, 0, "KASITA SEMINARY")
    c.restoreState()
    
    picha_logo = os.path.join(desktop_path, "logo.png")
    if os.path.exists(picha_logo):
        c.drawImage(picha_logo, 50, 730, width=60, height=60, mask='auto')
        
    c.setFont("Helvetica-Bold", 16)
    c.drawString(130, 760, "ST.FRANSIC JUNIOR SEMINARY-KASITA")
    c.setFillColorRGB(0, 0, 0) 
    c.setFont("Helvetica", 11)
    c.drawString(130, 740, "P.O.BOX 1234, ULANGA, MOROGORO")
    
    c.setStrokeColorRGB(0.5, 0.0, 0.0)
    c.setLineWidth(1.5)
    c.line(50, 715, 550, 715)
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(380, 685, f"Namba ya Risiti: {namba_risiti}")
    c.setFont("Helvetica", 10)
    c.drawString(370, 665, f"Tarehe/Muda: {muda_saa}")

    c.drawString(50, 685, f"ID ya Mwanafunzi: {m_id}")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 665, f"Jina Kamili: {jina.upper()}")
    c.setFont("Helvetica", 11) 
    c.drawString(50, 645, f"Darasa: {darasa}")
    
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.setLineWidth(0.5)
    c.line(50, 625, 550, 625)
    
    c.setFillColorRGB(0, 0, 0)

    ada_safi = str(ada).replace(',', '') if ada else "0"
    aliyolipa_safi = str(aliyolipa).replace(',', '')if aliyolipa else "0"
    deni_safi = str(deni).replace(',', '') if deni else "0"

    ada_formatted = format(float(ada_safi), ",.2f") 
    aliyolipa_formatted = format(float(aliyolipa_safi), ",.2f")
    deni_formatted = format(float(deni_safi), ",.2f")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, 600, "MAELEZO YA MALIPO")
    c.drawString(420, 600, "KIASI (TZS)")

    c.setFont("Helvetica", 11)
    c.drawString(50, 575, f"Ada Kamili ya Darasa ({darasa}):")
    c.drawString(420, 575, ada_formatted)

    c.drawString(50, 550, "Jumla Aliyokwisha Lipa:")
    c.drawString(420, 550, aliyolipa_formatted)
    
    c.line(50, 535, 550, 535)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 510, "DENI LILILOBAKI:")
    c.drawString(420, 510, f"TZS {deni_formatted}")
    
    c.setStrokeColorRGB(0.5, 0.0, 0.0)
    c.setLineWidth(1.2)
    c.line(50, 495, 550, 495)

    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, 420, "...............................................................")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, 405, "Sahihi ya Mhasibu / Bursar Signature")

    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(1)
    c.rect(380, 380, 150, 65, stroke=1, fill=0)
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.6, 0.6, 0.6)
    c.drawCentredString(455, 412, "[MHURI WA SHULE}")
                         
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(300, 310, "*Asante  kwa kuichagua KASITA SEMINARY. ELIMU NI UFUNGUO WA MAISHA.*")

    c.save()
    messagebox.showinfo("PDF Imepakizwa", f"Stakabadhi imetengenezwa: {os.path.abspath(pdf_name)}")

root = tk.Tk()
root.title("Mfumo wa kijanja wa Usimamizi wa Ada - Shule Bora n2.0")
root.geometry("1000x650")
root.config(bg="#f4f6f9")

lbl_title = tk.Label(root, text="MFUMO WA USIMAMIZI WA ADA (NOAH 2.0)", font=("Arial", 16, "bold"), bg="#1a2a6c", fg="white", pady=10)
lbl_title.pack(fill=tk.X)

frame_dash = tk.Frame(root, bg="#f4f6f9")
frame_dash.pack(fill=tk.X, padx=20, pady=10)

box1 = tk.Frame(frame_dash, bg="#00b4bd", bd=2, padx=10, pady=10)
box1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
tk.Label(box1, text="ADA INAYOTARAJIWA", font=("Arial", 10, "bold"), bg="#00b4bd", fg="white"). pack()
lbl_dash_ada = tk.Label(box1, text="TZS 0", font=("Arial", 14, "bold"), bg="#00b4bd", fg="white")
lbl_dash_ada.pack(pady=5)

box2 = tk.Frame(frame_dash, bg="#11998e", bd=2, padx=10, pady=10)
box2.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
tk.Label(box2, text="KIASI KILICHOKUSANYWA", font=("Arial", 10, "bold"), bg="#11998e", fg="white").pack()
lbl_dash_pato = tk.Label(box2, text="TZS 0", font=("Arial", 14, "bold"), bg="#11998e", fg="white")
lbl_dash_pato.pack(pady=5)

box3 = tk.Frame(frame_dash, bg="#f857a6", bd=2, padx=10, pady=10)
box3.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
tk.Label(box3, text="JUMLA YA MADENI NJE", font=("Arial", 10, "bold"), bg="#f857a6", fg="white").pack()
lbl_dash_deni = tk.Label(box3, text="TZS 0", font=("Arial", 14, "bold"), bg="#f857a6", fg="white")
lbl_dash_deni.pack(pady=5)

frame_controls = tk.Frame(root, bg="#f4f6f9")
frame_controls.pack(fill=tk.X, padx=20, pady=10)

lbl_form = tk.Label(frame_controls, text="Ingiza Malipo", font=("Arial", 11, "bold"), bg="#f4f6f9")
lbl_form.grid(row=0, column=0, sticky=tk.W, pady=5)

tk.Label(frame_controls, text="ID Mwanafunzi:", bg="#f4f6f9").grid(row=0, column=1, padx=5)
entry_id = tk.Entry(frame_controls, width=10)
entry_id.grid(row=0, column=2, padx=5)

tk.Label(frame_controls, text="Kiasi (TZS):", bg="#f4f6f9").grid(row=0, column=3, padx=5)
entry_kiasi = tk.Entry(frame_controls, width=15)
entry_kiasi.grid(row=0, column=4, padx=5)

btn_lipa = tk.Button(frame_controls, text="Sajili Malipo", bg="#11998e", fg="white", font=("Arial", 10, "bold"), command=weka_malipo)
btn_lipa.grid(row=0, column=5, padx=10)

tk.Label(frame_controls, text="Tafuta Mwanafunzi:", font=("Arial", 10, "bold"), bg="#f4f6f9").grid(row=0, column=6, padx=20)
entry_tafuta = tk.Entry(frame_controls, width=20)
entry_tafuta.grid(row=0, column=7, padx=5)
entry_tafuta.bind("<KeyRelease>", lambda e: leta_data())

column = ("id", "jina", "darasa", "ada", "aliyolipa", "deni")
tree = ttk.Treeview(root,columns=column, show="headings")

tree.heading("id", text="ID")
tree.heading("jina", text="Mwanafunzi")
tree.heading("darasa", text="Darasa")
tree.heading("ada", text="Ada Kamili")
tree.heading("aliyolipa", text="Jumla Aliyolipa")
tree.heading("deni", text="Deni Lililobaki")

tree.column("id", width=50, anchor=tk.CENTER)
tree.column("jina", width=200)
tree.column("darasa", width=120)
tree.column("ada", width=130)
tree.column("aliyolipa", width=130)
tree.column("deni", width=130)

tree.tag_configure("deni", foreground="#d9534f", font=("Arial", 10, "bold"))
tree.tag_configure("safi", foreground="#5cb85c", font=("Arial", 10, "bold"))

tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
frame_buttons = tk. Frame(root, bg="#f4f6f9")
frame_buttons.pack(pady=10)

btn_refresh = tk.Button(frame_buttons, text="Vuta/Onyesha Data", font=("Arial", 11, "bold"), bg="#1a2a6c", fg="white", padx=15, command=leta_data)
btn_refresh.pack(side=tk.LEFT, padx=10)

btn_pdf = tk.Button(frame_buttons, text="Toa Stakabadhi (PDF)", font=("Arial", 11, "bold"), bg="#f857a6", fg="white", padx=15, command=toa_stakabadhi)
btn_pdf.pack(side=tk.LEFT,padx=10)

leta_data()
root.mainloop()
