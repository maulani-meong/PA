import psycopg2
import pandas as pd
from datetime import date, datetime

# ==========================================

# 1. KONEKSI DATABASE

# ==========================================

def connectDB():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="566556",
            dbname="Modull 3"
        )

        cur = conn.cursor()

        return conn, cur

    except Exception as error:
        print("Koneksi database gagal:", error)
        return None, None

# ==========================================

# 2. LOGIN

# ==========================================

def login():
    print("\n===== LOGIN SISTEM SEKOLAH =====")

    username = input("Username : ")
    password = input("Password : ")

    conn, cur = connectDB()

    if conn is None:
        return None

    try:
        # Memeriksa akun staf
        cur.execute("""
            SELECT id_staf, nama_staf, jabatan
            FROM staf
            WHERE username = %s AND password = %s
        """, (username, password))

        data_staf = cur.fetchone()

        # Memeriksa akun guru
        cur.execute("""
            SELECT id_guru, nama_guru
            FROM guru
            WHERE username = %s AND password = %s
        """, (username, password))

        data_guru = cur.fetchone()

        # Memeriksa akun wali murid
        cur.execute("""
            SELECT id_wali_murid, nama_wali_murid
            FROM wali_murid
            WHERE username = %s AND password = %s
        """, (username, password))

        data_wali = cur.fetchone()

        # Memeriksa identitas ganda
        jumlah_akun = sum([
            data_staf is not None,
            data_guru is not None,
            data_wali is not None
        ])

        if jumlah_akun > 1:
            print("\nAkun memiliki identitas ganda!")
            print("Silakan hubungi administrator.")
            return None

        # Jika login sebagai staf
        if data_staf:
            print("\nLogin berhasil!")
            print("Selamat datang,", data_staf[1])
            print("Jabatan:", data_staf[2])

            return {
                "role": "staf",
                "id": data_staf[0],
                "nama": data_staf[1],
                "jabatan": data_staf[2]
            }

        # Jika login sebagai guru
        elif data_guru:
            print("\nLogin berhasil!")
            print("Selamat datang,", data_guru[1])
            print("Status: Guru")

            return {
                "role": "guru",
                "id": data_guru[0],
                "nama": data_guru[1],
                "jabatan": "Guru"
            }

        # Jika login sebagai wali murid
        elif data_wali:
            print("\nLogin berhasil!")
            print("Selamat datang,", data_wali[1])
            print("Status: Wali Murid")

            return {
                "role": "wali_murid",
                "id": data_wali[0],
                "nama": data_wali[1],
                "jabatan": "Wali Murid"
            }

        else:
            print("\nUsername atau password salah!")
            return None

    except Exception as error:
        print("Terjadi kesalahan saat login:", error)
        return None

    finally:
        cur.close()
        conn.close()

# ==========================================

# 3. PROGRAM / MENU UTAMA

# ==========================================

# Fungsi main diletakkan di atas agar mudah ditemukan.

# Pemanggilannya tetap di bagian paling bawah agar semua menu sudah didefinisikan.

def main():
    while True:
            data = login()

            if data is None:
                print("\nUsername atau password salah.")
                print("Silakan login kembali.")
                continue

            if data["role"] == "staf":

                menu_staf(data)

            elif data["role"] == "guru":

                menu_guru(data)

            elif data["role"] == "wali_murid":

                menu_wali_murid(data)

            else:

                print("\nRole tidak dikenali!")
                continue

            # Program berhenti setelah pengguna logout
            print("\nProgram selesai. Terima kasih!")
            break

# ==================================
# RIWAYAT PRESENSI WALI MURID
# ==================================
def lihat_riwayat_presensi_wali(id_wali):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                s.nama_siswa,
                k.nama_kelas,
                p.tanggal,
                p.status_kehadiran,
                p.keterangan,
                mp.nama_mapel
            FROM presensi p
            JOIN siswa s ON p.id_siswa = s.id_siswa
            JOIN kelas k ON s.id_kelas = k.id_kelas
            JOIN jadwal j ON p.id_jadwal = j.id_jadwal
            JOIN mata_pelajaran mp ON j.id_mapel = mp.id_mapel
            WHERE s.id_wali_murid = %s
            ORDER BY p.tanggal DESC
        """, (id_wali,))

        data = cur.fetchall()

        if data:
            kolom = [
                "Nama Siswa",
                "Kelas",
                "Tanggal",
                "Status",
                "Keterangan",
                "Mata Pelajaran"
            ]

            df = pd.DataFrame(data, columns=kolom)

            print("\n===== RIWAYAT PRESENSI SISWA =====")
            print(df.to_string(index=False))

        else:
            print("\nBelum ada riwayat presensi.")

    except Exception as error:
        print("Gagal menampilkan presensi:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# NILAI AKADEMIK WALI MURID
# ==================================
def lihat_nilai_akademik_wali(id_wali):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                s.nis,
                s.nama_siswa,
                k.nama_kelas,
                n.semester,
                n.tahun_ajaran,
                n.nilai_tugas,
                n.nilai_uts,
                n.nilai_uas,
                ROUND(
                    (n.nilai_tugas + n.nilai_uts + n.nilai_uas) / 3.0,
                    2
                ) AS nilai_akhir,
                g.nama_guru
            FROM nilai_akademik n
            JOIN siswa s ON n.id_siswa = s.id_siswa
            JOIN kelas k ON s.id_kelas = k.id_kelas
            JOIN guru g ON n.id_guru = g.id_guru
            WHERE s.id_wali_murid = %s
            ORDER BY s.nama_siswa, n.tahun_ajaran DESC, n.semester
        """, (id_wali,))

        data = cur.fetchall()

        if data:
            kolom = [
                "NIS",
                "Nama Siswa",
                "Kelas",
                "Semester",
                "Tahun Ajaran",
                "Nilai Tugas",
                "Nilai UTS",
                "Nilai UAS",
                "Nilai Akhir",
                "Guru"
            ]

            df = pd.DataFrame(data, columns=kolom)

            print("\n===== NILAI AKADEMIK SISWA =====")
            print(df.to_string(index=False))

        else:
            print("\nBelum ada nilai akademik.")

    except Exception as error:
        print("Gagal menampilkan nilai akademik:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# MELIHAT SEMUA DATA PRESENSI (STAF)
# ==================================
def lihat_semua_presensi_staf():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                s.nis,
                s.nama_siswa,
                k.nama_kelas,
                p.tanggal,
                mp.nama_mapel,
                p.status_kehadiran,
                p.keterangan,
                g.nama_guru
            FROM presensi p
            JOIN siswa s ON p.id_siswa = s.id_siswa
            JOIN kelas k ON s.id_kelas = k.id_kelas
            JOIN jadwal j ON p.id_jadwal = j.id_jadwal
            JOIN mata_pelajaran mp ON j.id_mapel = mp.id_mapel
            JOIN guru g ON p.id_guru = g.id_guru
            ORDER BY p.tanggal DESC, s.nama_siswa
        """)

        data = cur.fetchall()

        if data:
            kolom = [
                "NIS",
                "Nama Siswa",
                "Kelas",
                "Tanggal",
                "Mata Pelajaran",
                "Status",
                "Keterangan",
                "Guru"
            ]

            df = pd.DataFrame(data, columns=kolom)

            print("\n===== SELURUH DATA PRESENSI SISWA =====")
            print(df.to_string(index=False))

        else:
            print("\nBelum ada data presensi.")

    except Exception as error:
        print("Gagal menampilkan presensi:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# MELIHAT SEMUA NILAI AKADEMIK (STAF)
# ==================================
def lihat_semua_nilai_staf():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                s.nis,
                s.nama_siswa,
                k.nama_kelas,
                n.semester,
                n.tahun_ajaran,
                n.nilai_tugas,
                n.nilai_uts,
                n.nilai_uas,
                ROUND(
                    (n.nilai_tugas + n.nilai_uts + n.nilai_uas) / 3.0,
                    2
                ) AS nilai_akhir,
                g.nama_guru
            FROM nilai_akademik n
            JOIN siswa s ON n.id_siswa = s.id_siswa
            JOIN kelas k ON s.id_kelas = k.id_kelas
            JOIN guru g ON n.id_guru = g.id_guru
            ORDER BY s.nama_siswa, n.tahun_ajaran DESC
        """)

        data = cur.fetchall()

        if data:
            kolom = [
                "NIS",
                "Nama Siswa",
                "Kelas",
                "Semester",
                "Tahun Ajaran",
                "Nilai Tugas",
                "Nilai UTS",
                "Nilai UAS",
                "Nilai Akhir",
                "Guru"
            ]

            df = pd.DataFrame(data, columns=kolom)

            print("\n===== SELURUH NILAI AKADEMIK SISWA =====")
            print(df.to_string(index=False))

        else:
            print("\nBelum ada nilai akademik.")

    except Exception as error:
        print("Gagal menampilkan nilai akademik:", error)

    finally:
        cur.close()
        conn.close()








# ==================================
# 1. MENAMPILKAN DATA GURU
# ==================================
def tampilkan_guru():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                g.id_guru,
                g.nama_guru,
                g.nip,
                g.jenis_kelamin,
                g.tanggal_lahir,
                g.no_telepon,
                g.email,
                g.username,
                a.nama_wilayah
            FROM guru g
            JOIN alamat a ON g.id_alamat = a.id_alamat
            ORDER BY g.id_guru
        """)

        data = cur.fetchall()

        if data:
            kolom = [
                "ID Guru",
                "Nama Guru",
                "NIP",
                "Jenis Kelamin",
                "Tanggal Lahir",
                "No Telepon",
                "Email",
                "Username",
                "Alamat"
            ]

            df = pd.DataFrame(data, columns=kolom)
            print("\n===== DATA GURU =====")
            print(df.to_string(index=False))
        else:
            print("Data guru masih kosong.")

    except Exception as error:
        print("Gagal menampilkan data guru:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 2. MENAMBAH DATA GURU
# ==================================
def tambah_guru():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        print("\n===== DAFTAR ALAMAT =====")

        cur.execute("""
            SELECT id_alamat, nama_wilayah
            FROM alamat
            ORDER BY id_alamat
        """)

        data_alamat = cur.fetchall()

        for alamat in data_alamat:
            print(f"{alamat[0]}. {alamat[1]}")

        print("\n===== TAMBAH DATA GURU =====")

        nama = input("Nama Guru       : ")
        nip = input("NIP             : ")
        jk = input("Jenis Kelamin (L/P): ").upper()
        tanggal = input("Tanggal Lahir (YYYY-MM-DD): ")
        telepon = input("No Telepon      : ")
        email = input("Email           : ")
        username = input("Username        : ")
        password = input("Password        : ")
        id_alamat = input("ID Alamat       : ")

        if jk not in ["L", "P"]:
            print("Jenis kelamin harus L atau P!")
            return

        cur.execute("""
            INSERT INTO guru
            (nama_guru, nip, jenis_kelamin, tanggal_lahir,
             no_telepon, email, username, password, id_alamat)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nama, nip, jk, tanggal, telepon,
            email, username, password, id_alamat
        ))

        conn.commit()
        print("\nData guru berhasil ditambahkan!")

    except Exception as error:
        conn.rollback()
        print("Gagal menambahkan data guru:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 3. MENGUBAH DATA GURU
# ==================================
def ubah_guru():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_guru()

        id_guru = input("\nMasukkan ID Guru yang ingin diubah: ")

        cur.execute("""
            SELECT * FROM guru
            WHERE id_guru = %s
        """, (id_guru,))

        data = cur.fetchone()

        if data is None:
            print("ID Guru tidak ditemukan!")
            return

        print("\n===== UBAH DATA GURU =====")
        print("Kosongkan input jika tidak ingin mengubah nilai.")

        nama = input(f"Nama Guru [{data[1]}]: ") or data[1]
        nip = input(f"NIP [{data[2]}]: ") or data[2]
        jk = input(f"Jenis Kelamin [{data[3]}]: ").upper() or data[3]
        tanggal = input(f"Tanggal Lahir [{data[4]}]: ") or data[4]
        telepon = input(f"No Telepon [{data[5]}]: ") or data[5]
        email = input(f"Email [{data[6]}]: ") or data[6]
        username = input(f"Username [{data[7]}]: ") or data[7]
        password = input(f"Password [{data[8]}]: ") or data[8]

        print("\n===== DAFTAR ALAMAT =====")
        cur.execute("""
            SELECT id_alamat, nama_wilayah
            FROM alamat
            ORDER BY id_alamat
        """)

        data_alamat = cur.fetchall()

        for alamat in data_alamat:
            print(f"{alamat[0]}. {alamat[1]}")

        id_alamat = input(f"ID Alamat [{data[9]}]: ") or data[9]

        if jk not in ["L", "P"]:
            print("Jenis kelamin harus L atau P!")
            return

        cur.execute("""
            UPDATE guru
            SET nama_guru = %s,
                nip = %s,
                jenis_kelamin = %s,
                tanggal_lahir = %s,
                no_telepon = %s,
                email = %s,
                username = %s,
                password = %s,
                id_alamat = %s
            WHERE id_guru = %s
        """, (
            nama, nip, jk, tanggal, telepon,
            email, username, password, id_alamat, id_guru
        ))

        conn.commit()
        print("\nData guru berhasil diubah!")

    except Exception as error:
        conn.rollback()
        print("Gagal mengubah data guru:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 4. MENGHAPUS DATA GURU
# ==================================
def hapus_guru():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_guru()

        id_guru = input("\nMasukkan ID Guru yang ingin dihapus: ")

        cur.execute("""
            SELECT nama_guru
            FROM guru
            WHERE id_guru = %s
        """, (id_guru,))

        data = cur.fetchone()

        if data is None:
            print("ID Guru tidak ditemukan!")
            return

        print(f"\nNama Guru: {data[0]}")
        konfirmasi = input("Yakin ingin menghapus data ini? (y/n): ")

        if konfirmasi.lower() == "y":
            cur.execute("""
                DELETE FROM guru
                WHERE id_guru = %s
            """, (id_guru,))

            conn.commit()
            print("Data guru berhasil dihapus!")
        else:
            print("Penghapusan dibatalkan.")

    except Exception as error:
        conn.rollback()
        print("Gagal menghapus data guru:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 5. MELIHAT DATA GURU SENDIRI
# ==================================
def lihat_data_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                g.id_guru,
                g.nama_guru,
                g.nip,
                g.jenis_kelamin,
                g.tanggal_lahir,
                g.no_telepon,
                g.email,
                g.username,
                a.nama_wilayah
            FROM guru g
            JOIN alamat a ON g.id_alamat = a.id_alamat
            WHERE g.id_guru = %s
        """, (id_guru,))

        data = cur.fetchone()

        if data:
            kolom = [
                "ID Guru",
                "Nama Guru",
                "NIP",
                "Jenis Kelamin",
                "Tanggal Lahir",
                "No Telepon",
                "Email",
                "Username",
                "Alamat"
            ]

            df = pd.DataFrame([data], columns=kolom)

            print("\n===== DATA PROFIL GURU =====")
            print(df.to_string(index=False))

        else:
            print("\nData guru tidak ditemukan!")

    except Exception as error:
        print("Gagal menampilkan data guru:", error)

    finally:
        cur.close()
        conn.close()




# ==================================
# 1. MENAMPILKAN DATA JADWAL
# ==================================
def tampilkan_jadwal():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                j.id_jadwal,
                j.hari,
                j.tanggal,
                j.jam_mulai,
                j.jam_selesai,
                m.nama_mapel,
                k.nama_kelas
            FROM jadwal j
            JOIN mata_pelajaran m
                ON j.id_mapel = m.id_mapel
            JOIN kelas k
                ON j.id_kelas = k.id_kelas
            ORDER BY j.tanggal, j.jam_mulai, k.id_kelas
        """)

        data = cur.fetchall()

        if data:
            kolom = [
                "ID Jadwal",
                "Hari",
                "Tanggal",
                "Jam Mulai",
                "Jam Selesai",
                "Mata Pelajaran",
                "Kelas"
            ]

            df = pd.DataFrame(data, columns=kolom)

            print("\n===== DATA JADWAL PELAJARAN =====")
            print(df.to_string(index=False))

        else:
            print("Data jadwal masih kosong.")

    except Exception as error:
        print("Gagal menampilkan jadwal:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 2. MENAMBAH DATA JADWAL
# ==================================
def tambah_jadwal():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        print("\n===== DAFTAR MATA PELAJARAN =====")

        cur.execute("""
            SELECT id_mapel, nama_mapel
            FROM mata_pelajaran
            ORDER BY id_mapel
        """)

        data_mapel = cur.fetchall()

        if not data_mapel:
            print("Data mata pelajaran belum tersedia!")
            return

        for mapel in data_mapel:
            print(f"{mapel[0]}. {mapel[1]}")

        print("\n===== DAFTAR KELAS =====")

        cur.execute("""
            SELECT id_kelas, nama_kelas
            FROM kelas
            ORDER BY id_kelas
        """)

        data_kelas = cur.fetchall()

        if not data_kelas:
            print("Data kelas belum tersedia!")
            return

        for kelas in data_kelas:
            print(f"{kelas[0]}. {kelas[1]}")

        print("\n===== TAMBAH JADWAL =====")

        hari = input("Hari: ").capitalize()
        tanggal = input("Tanggal (YYYY-MM-DD): ")
        jam_mulai = input("Jam Mulai (HH:MM): ")
        jam_selesai = input("Jam Selesai (HH:MM): ")
        id_mapel = input("ID Mata Pelajaran: ")
        id_kelas = input("ID Kelas: ")

        if hari not in [
            "Senin", "Selasa", "Rabu",
            "Kamis", "Jumat", "Sabtu"
        ]:
            print("Hari tidak valid!")
            return

        cur.execute("""
            INSERT INTO jadwal
            (hari, tanggal, jam_mulai, jam_selesai,
             id_mapel, id_kelas)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            hari, tanggal, jam_mulai,
            jam_selesai, id_mapel, id_kelas
        ))

        conn.commit()
        print("\nJadwal berhasil ditambahkan!")

    except Exception as error:
        conn.rollback()
        print("Gagal menambahkan jadwal:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 3. MENGUBAH DATA JADWAL
# ==================================
def ubah_jadwal():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_jadwal()

        id_jadwal = input("\nMasukkan ID Jadwal: ")

        cur.execute("""
            SELECT *
            FROM jadwal
            WHERE id_jadwal = %s
        """, (id_jadwal,))

        data = cur.fetchone()

        if data is None:
            print("ID Jadwal tidak ditemukan!")
            return

        print("\n===== UBAH DATA JADWAL =====")
        print("Kosongkan input jika tidak ingin mengubah data.")

        hari = input(f"Hari [{data[1]}]: ") or data[1]
        tanggal = input(f"Tanggal [{data[2]}]: ") or data[2]
        jam_mulai = input(f"Jam Mulai [{data[3]}]: ") or data[3]
        jam_selesai = input(f"Jam Selesai [{data[4]}]: ") or data[4]

        print("\n===== DAFTAR MATA PELAJARAN =====")

        cur.execute("""
            SELECT id_mapel, nama_mapel
            FROM mata_pelajaran
            ORDER BY id_mapel
        """)

        for mapel in cur.fetchall():
            print(f"{mapel[0]}. {mapel[1]}")

        id_mapel = input(f"ID Mapel [{data[5]}]: ") or data[5]

        print("\n===== DAFTAR KELAS =====")

        cur.execute("""
            SELECT id_kelas, nama_kelas
            FROM kelas
            ORDER BY id_kelas
        """)

        for kelas in cur.fetchall():
            print(f"{kelas[0]}. {kelas[1]}")

        id_kelas = input(f"ID Kelas [{data[6]}]: ") or data[6]

        hari = hari.capitalize()

        if hari not in [
            "Senin", "Selasa", "Rabu",
            "Kamis", "Jumat", "Sabtu"
        ]:
            print("Hari tidak valid!")
            return

        cur.execute("""
            UPDATE jadwal
            SET hari = %s,
                tanggal = %s,
                jam_mulai = %s,
                jam_selesai = %s,
                id_mapel = %s,
                id_kelas = %s
            WHERE id_jadwal = %s
        """, (
            hari, tanggal, jam_mulai,
            jam_selesai, id_mapel,
            id_kelas, id_jadwal
        ))

        conn.commit()
        print("\nJadwal berhasil diubah!")

    except Exception as error:
        conn.rollback()
        print("Gagal mengubah jadwal:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 4. MENGHAPUS DATA JADWAL
# ==================================
def hapus_jadwal():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_jadwal()

        id_jadwal = input("\nMasukkan ID Jadwal: ")

        cur.execute("""
            SELECT
                j.hari,
                j.tanggal,
                j.jam_mulai,
                m.nama_mapel,
                k.nama_kelas
            FROM jadwal j
            JOIN mata_pelajaran m
                ON j.id_mapel = m.id_mapel
            JOIN kelas k
                ON j.id_kelas = k.id_kelas
            WHERE j.id_jadwal = %s
        """, (id_jadwal,))

        data = cur.fetchone()

        if data is None:
            print("ID Jadwal tidak ditemukan!")
            return

        print("\n===== DETAIL JADWAL =====")
        print("Hari:", data[0])
        print("Tanggal:", data[1])
        print("Jam:", data[2])
        print("Mata Pelajaran:", data[3])
        print("Kelas:", data[4])

        konfirmasi = input(
            "\nYakin ingin menghapus jadwal ini? (y/n): "
        )

        if konfirmasi.lower() == "y":

            cur.execute("""
                DELETE FROM jadwal
                WHERE id_jadwal = %s
            """, (id_jadwal,))

            conn.commit()
            print("Jadwal berhasil dihapus!")

        else:
            print("Penghapusan dibatalkan.")

    except Exception as error:
        conn.rollback()
        print("Gagal menghapus jadwal:", error)

    finally:
        cur.close()
        conn.close()








# ==================================
# 1. MENAMPILKAN DATA MATA PELAJARAN
# ==================================
def tampilkan_mapel():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                m.id_mapel,
                m.nama_mapel,
                g.nama_guru
            FROM mata_pelajaran m
            JOIN guru g ON m.id_guru = g.id_guru
            ORDER BY m.id_mapel
        """)

        data = cur.fetchall()

        if data:
            kolom = ["ID Mapel", "Nama Mata Pelajaran", "Nama Guru"]
            df = pd.DataFrame(data, columns=kolom)

            print("\n===== DATA MATA PELAJARAN =====")
            print(df.to_string(index=False))
        else:
            print("Data mata pelajaran masih kosong.")

    except Exception as error:
        print("Gagal menampilkan data:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 2. MENAMBAH MATA PELAJARAN
# ==================================
def tambah_mapel():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        print("\n===== DAFTAR GURU =====")

        cur.execute("""
            SELECT id_guru, nama_guru
            FROM guru
            ORDER BY id_guru
        """)

        data_guru = cur.fetchall()

        if not data_guru:
            print("Belum ada data guru!")
            return

        for guru in data_guru:
            print(f"{guru[0]}. {guru[1]}")

        print("\n===== TAMBAH MATA PELAJARAN =====")

        nama_mapel = input("Nama Mata Pelajaran: ")
        id_guru = input("ID Guru: ")

        cur.execute("""
            INSERT INTO mata_pelajaran (nama_mapel, id_guru)
            VALUES (%s, %s)
        """, (nama_mapel, id_guru))

        conn.commit()
        print("\nMata pelajaran berhasil ditambahkan!")

    except Exception as error:
        conn.rollback()
        print("Gagal menambahkan data:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 3. MENGUBAH MATA PELAJARAN
# ==================================
def ubah_mapel():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_mapel()

        id_mapel = input("\nMasukkan ID Mata Pelajaran: ")

        cur.execute("""
            SELECT id_mapel, nama_mapel, id_guru
            FROM mata_pelajaran
            WHERE id_mapel = %s
        """, (id_mapel,))

        data = cur.fetchone()

        if data is None:
            print("ID Mata Pelajaran tidak ditemukan!")
            return

        print("\n===== UBAH MATA PELAJARAN =====")

        nama_mapel = input(
            f"Nama Mata Pelajaran [{data[1]}]: "
        ) or data[1]

        print("\n===== DAFTAR GURU =====")

        cur.execute("""
            SELECT id_guru, nama_guru
            FROM guru
            ORDER BY id_guru
        """)

        data_guru = cur.fetchall()

        for guru in data_guru:
            print(f"{guru[0]}. {guru[1]}")

        id_guru = input(
            f"ID Guru [{data[2]}]: "
        ) or data[2]

        cur.execute("""
            UPDATE mata_pelajaran
            SET nama_mapel = %s,
                id_guru = %s
            WHERE id_mapel = %s
        """, (nama_mapel, id_guru, id_mapel))

        conn.commit()
        print("\nMata pelajaran berhasil diubah!")

    except Exception as error:
        conn.rollback()
        print("Gagal mengubah data:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 4. MENGHAPUS MATA PELAJARAN
# ==================================
def hapus_mapel():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_mapel()

        id_mapel = input("\nMasukkan ID Mata Pelajaran: ")

        cur.execute("""
            SELECT nama_mapel
            FROM mata_pelajaran
            WHERE id_mapel = %s
        """, (id_mapel,))

        data = cur.fetchone()

        if data is None:
            print("ID Mata Pelajaran tidak ditemukan!")
            return

        print(f"\nNama Mata Pelajaran: {data[0]}")

        konfirmasi = input(
            "Yakin ingin menghapus data ini? (y/n): "
        )

        if konfirmasi.lower() == "y":
            cur.execute("""
                DELETE FROM mata_pelajaran
                WHERE id_mapel = %s
            """, (id_mapel,))

            conn.commit()
            print("Mata pelajaran berhasil dihapus!")

        else:
            print("Penghapusan dibatalkan.")

    except Exception as error:
        conn.rollback()
        print("Gagal menghapus data:", error)

    finally:
        cur.close()
        conn.close()






def menu_guru(data):

    id_guru = data["id"]

    while True:

        print("\n================================")
        print("          MENU UTAMA GURU       ")
        print("================================")

        print("Selamat datang", data["nama"])
        print("Status:", data["jabatan"])

        print("\n1. Lihat Data Guru")
        print("2. Lihat Data Siswa")
        print("3. Mengelola Data Presensi")
        print("4. Mengelola Nilai Akademik")
        print("0. Logout")

        pilih = input("\nPilih menu: ")

        match pilih:

            case "1":
                lihat_data_guru(id_guru)

            case "2":
                lihat_siswa_guru(id_guru)

            case "3":
                menu_presensi_guru(id_guru)

            case "4":
                menu_nilai_guru(id_guru)

            case "0":
                print("\nLogout berhasil")
                return

            case _:
                print("\nPilihan Tidak Tersedia!")
        input("\nTekan Enter untuk kembali ke menu...")




def menu_nilai_guru(id_guru):

    while True:

        print("\n================================")
        print("      MENU NILAI AKADEMIK")
        print("================================")

        print("1. Tambah Nilai")
        print("2. Tampilkan Nilai")
        print("3. Ubah Nilai")
        print("4. Hapus Nilai")
        print("0. Kembali")

        pilih = input("\nPilih menu: ")

        match pilih:

            case "1":
                tambah_nilai_guru(id_guru)

            case "2":
                tampilkan_nilai_guru(id_guru)

            case "3":
                ubah_nilai_guru(id_guru)

            case "4":
                hapus_nilai_guru(id_guru)

            case "0":
                print("\nKembali ke menu Guru.")
                break

            case _:
                print("\nPilihan tidak tersedia!")
        input("\nTekan Enter untuk kembali ke menu...")




def menu_presensi_guru(id_guru):

    while True:

        print("\n================================")
        print("       MENU KELOLA PRESENSI")
        print("================================")

        print("1. Tambah Presensi")
        print("2. Tampilkan Presensi")
        print("3. Ubah Presensi")
        print("4. Hapus Presensi")
        print("0. Kembali")

        pilih = input("\nPilih menu: ")

        match pilih:

            case "1":
                tambah_presensi_guru(id_guru)

            case "2":
                tampilkan_presensi_guru(id_guru)

            case "3":
                ubah_presensi_guru(id_guru)

            case "4":
                hapus_presensi_guru(id_guru)

            case "0":
                print("\nKembali ke menu Guru.")
                break

            case _:
                print("\nPilihan tidak tersedia!")
        input("\nTekan Enter untuk kembali ke menu...")













def menu_staf(data):

    # Mengambil ID staf yang sedang login
    id_staf = data["id"]

    while True:

        print("\n================================")
        print("         MENU UTAMA STAF")
        print("================================")

        print("Selamat datang,", data["nama"])
        print("Jabatan:", data["jabatan"])

        print("\n1. Kelola Data Wali Murid")
        print("2. Kelola Data Siswa")
        print("3. Kelola Data Guru")
        print("4. Kelola Mata Pelajaran")
        print("5. Kelola Jadwal")
        print("6. Lihat Data Presensi")
        print("7. Lihat Nilai Akademik")
        print("8. Kelola Transaksi SPP")
        print("9. Kelola Data Staf")
        print("0. Logout")

        pilih = input("\nPilih menu: ")

        match pilih:

            # =========================
            # 1. DATA WALI MURID
            # =========================
            case "1":
                while True:

                    print("\n===== MENU WALI MURID =====")
                    print("1. Tambah Wali Murid")
                    print("2. Lihat Wali Murid")
                    print("3. Ubah Wali Murid")
                    print("4. Hapus Wali Murid")
                    print("0. Kembali")

                    pilih = input("\nPilih menu: ")

                    match pilih:
                        case "1":
                            tambah_wali_murid()

                        case "2":
                            tampilkan_wali_murid()

                        case "3":
                            ubah_wali_murid()

                        case "4":
                            hapus_wali_murid()

                        case "0":
                            break

                        case _:
                            print("Pilihan tidak tersedia!")
                    input("\nTekan Enter untuk kembali ke menu...")

            # =========================
            # 2. DATA SISWA
            # =========================
            case "2":
                while True:

                    print("\n===== MENU DATA SISWA =====")
                    print("1. Tambah Siswa")
                    print("2. Lihat Siswa")
                    print("3. Ubah Siswa")
                    print("4. Hapus Siswa")
                    print("0. Kembali")

                    pilih = input("\nPilih menu: ")

                    match pilih:
                        case "1":
                            tambah_siswa()

                        case "2":
                            tampilkan_siswa()

                        case "3":
                            ubah_siswa()

                        case "4":
                            hapus_siswa()

                        case "0":
                            break

                        case _:
                            print("Pilihan tidak tersedia!")
                    input("\nTekan Enter untuk kembali ke menu...")

            # =========================
            # 3. DATA GURU
            # =========================
            case "3":
                while True:

                    print("\n===== MENU DATA GURU =====")
                    print("1. Tambah Guru")
                    print("2. Tampilkan Guru")
                    print("3. Ubah Guru")
                    print("4. Hapus Guru")
                    print("0. Kembali")

                    pilih = input("\nPilih menu: ")

                    match pilih:
                        case "1":
                            tambah_guru()

                        case "2":
                            tampilkan_guru()

                        case "3":
                            ubah_guru()

                        case "4":
                            hapus_guru()

                        case "0":
                            break

                        case _:
                            print("Pilihan tidak tersedia!")
                    input("\nTekan Enter untuk kembali ke menu...")

            # =========================
            # 4. DATA MATA PELAJARAN
            # =========================
            case "4":
                while True:

                    print("\n===== MENU MATA PELAJARAN =====")
                    print("1. Tambah Mata Pelajaran")
                    print("2. Tampilkan Mata Pelajaran")
                    print("3. Ubah Mata Pelajaran")
                    print("4. Hapus Mata Pelajaran")
                    print("0. Kembali")

                    pilih = input("\nPilih menu: ")

                    match pilih:
                        case "1":
                            tambah_mapel()

                        case "2":
                            tampilkan_mapel()

                        case "3":
                            ubah_mapel()

                        case "4":
                            hapus_mapel()

                        case "0":
                            break

                        case _:
                            print("Pilihan tidak tersedia!")
                    input("\nTekan Enter untuk kembali ke menu...")

            # =========================
            # 5. DATA JADWAL
            # =========================
            case "5":
                while True:

                    print("\n===== MENU JADWAL =====")
                    print("1. Tambah Jadwal")
                    print("2. Tampilkan Jadwal")
                    print("3. Ubah Jadwal")
                    print("4. Hapus Jadwal")
                    print("0. Kembali")

                    pilih = input("\nPilih menu: ")

                    match pilih:
                        case "1":
                            tambah_jadwal()

                        case "2":
                            tampilkan_jadwal()

                        case "3":
                            ubah_jadwal()

                        case "4":
                            hapus_jadwal()

                        case "0":
                            break

                        case _:
                            print("Pilihan tidak tersedia!")
                    input("\nTekan Enter untuk kembali ke menu...")

            # =========================
            # 6. DATA PRESENSI
            # =========================
            case "6":
                lihat_semua_presensi_staf()

            # =========================
            # 7. NILAI AKADEMIK
            # =========================
            case "7":
                lihat_semua_nilai_staf()

            # =========================
            # 8. TRANSAKSI SPP
            # =========================
            case "8":
                menu_transaksi_spp(id_staf)

            # =========================
            # 9. DATA STAF
            # =========================
            case "9":
                while True:

                    print("\n===== MENU DATA STAF =====")
                    print("1. Tambah Staf")
                    print("2. Tampilkan Staf")
                    print("3. Ubah Staf")
                    print("4. Hapus Staf")
                    print("0. Kembali")

                    pilih = input("\nPilih menu: ")

                    match pilih:
                        case "1":
                            tambah_staf()

                        case "2":
                            tampilkan_staf()

                        case "3":
                            ubah_staf()

                        case "4":
                            hapus_staf()

                        case "0":
                            break

                        case _:
                            print("Pilihan tidak tersedia!")
                    input("\nTekan Enter untuk kembali ke menu...")

            # =========================
            # 0. LOGOUT
            # =========================
            case "0":
                print("\nLogout berhasil!")
                return

            case _:
                print("\nPilihan tidak tersedia!")
        input("\nTekan Enter untuk kembali ke menu...")

def menu_transaksi_spp(id_staf):

    while True:
        print("\n===== MENU TRANSAKSI SPP =====")
        print("1. Tambah Tagihan SPP")
        print("2. Tampilkan Tagihan SPP")
        print("3. Tambah Transaksi")
        print("4. Tampilkan Transaksi")
        print("5. Ubah Transaksi")
        print("6. Hapus Transaksi")
        print("0. Kembali")

        pilih = input("\nPilih menu: ")

        match pilih:
            case "1":
                tambah_tagihan()

            case "2":
                tampilkan_tagihan()

            case "3":
                tambah_transaksi(id_staf)

            case "4":
                tampilkan_transaksi()

            case "5":
                ubah_transaksi()

            case "6":
                hapus_transaksi()

            case "0":
                print("Kembali ke menu utama.")
                break

            case _:
                print("Pilihan tidak valid!")
        input("\nTekan Enter untuk kembali ke menu...")





def menu_wali_murid(data):

    id_wali = data["id"]

    while True:

        print("\n================================")
        print("       MENU UTAMA WALI MURID")
        print("================================")

        print("Selamat datang,", data["nama"])
        print("Status:", data["jabatan"])

        print("\n1. Lihat Data Wali Murid")
        print("2. Lihat Data Siswa")
        print("3. Lihat Tagihan SPP")
        print("4. Lihat Bukti Transaksi")
        print("5. Lihat Riwayat Presensi")
        print("6. Lihat Nilai Akademik")
        print("0. Logout")

        pilih = input("\nPilih menu: ")

        match pilih:

            case "1":
                lihat_data_wali_murid(id_wali)

            case "2":
                lihat_siswa_wali(id_wali)

            case "3":
                tampilkan_tagihan_wali(id_wali)

            case "4":
                lihat_riwayat_transaksi_wali(id_wali)

            case "5":
                lihat_riwayat_presensi_wali(id_wali)

            case "6":
                lihat_nilai_akademik_wali(id_wali)

            case "0":
                print("\nLogout berhasil!")
                return

            case _:
                print("\nPilihan tidak tersedia!")
        input("\nTekan Enter untuk kembali ke menu...")




# ==================================
# 1. MENAMPILKAN NILAI GURU
# ==================================
def tampilkan_nilai_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                n.id_nilai_akademik,
                s.nis,
                s.nama_siswa,
                n.semester,
                n.tahun_ajaran,
                n.nilai_tugas,
                n.nilai_uts,
                n.nilai_uas,
                ROUND(
                    (n.nilai_tugas + n.nilai_uts + n.nilai_uas) / 3.0,
                    2
                ) AS nilai_akhir
            FROM nilai_akademik n
            JOIN siswa s
                ON n.id_siswa = s.id_siswa
            WHERE n.id_guru = %s
            ORDER BY n.tahun_ajaran DESC, s.nama_siswa
        """, (id_guru,))

        data = cur.fetchall()

        if data:
            kolom = [
                "ID Nilai",
                "NIS",
                "Nama Siswa",
                "Semester",
                "Tahun Ajaran",
                "Nilai Tugas",
                "Nilai UTS",
                "Nilai UAS",
                "Nilai Akhir"
            ]

            df = pd.DataFrame(data, columns=kolom)

            print("\n===== DATA NILAI AKADEMIK =====")
            print(df.to_string(index=False))

        else:
            print("\nBelum ada data nilai akademik.")

    except Exception as error:
        print("Gagal menampilkan nilai:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 2. MENAMBAH NILAI AKADEMIK
# ==================================
def tambah_nilai_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        # Menampilkan siswa yang diajar oleh Guru
        cur.execute("""
            SELECT DISTINCT
                s.id_siswa,
                s.nis,
                s.nama_siswa,
                k.nama_kelas
            FROM siswa s
            JOIN kelas k
                ON s.id_kelas = k.id_kelas
            JOIN jadwal j
                ON s.id_kelas = j.id_kelas
            JOIN mata_pelajaran mp
                ON j.id_mapel = mp.id_mapel
            WHERE mp.id_guru = %s
            ORDER BY s.nama_siswa
        """, (id_guru,))

        data_siswa = cur.fetchall()

        if not data_siswa:
            print("\nGuru belum memiliki siswa yang diajar.")
            return

        kolom = [
            "ID Siswa",
            "NIS",
            "Nama Siswa",
            "Kelas"
        ]

        print("\n===== DAFTAR SISWA =====")
        print(pd.DataFrame(
            data_siswa,
            columns=kolom
        ).to_string(index=False))

        id_siswa = input("\nMasukkan ID Siswa: ")

        # Memastikan siswa benar-benar diajar Guru
        cur.execute("""
            SELECT s.id_siswa
            FROM siswa s
            JOIN jadwal j
                ON s.id_kelas = j.id_kelas
            JOIN mata_pelajaran mp
                ON j.id_mapel = mp.id_mapel
            WHERE s.id_siswa = %s
              AND mp.id_guru = %s
            LIMIT 1
        """, (id_siswa, id_guru))

        if cur.fetchone() is None:
            print("\nSiswa tidak ditemukan atau bukan siswa yang diajar!")
            return

        print("\n===== TAMBAH NILAI AKADEMIK =====")

        semester = input("Semester (Ganjil/Genap): ").capitalize()

        if semester not in ["Ganjil", "Genap"]:
            print("\nSemester harus Ganjil atau Genap!")
            return

        tahun_ajaran = input("Tahun Ajaran (contoh 2026/2027): ")

        if len(tahun_ajaran) > 10 or not tahun_ajaran:
            print("\nFormat tahun ajaran tidak valid!")
            return

        nilai_tugas = int(input("Nilai Tugas: "))
        nilai_uts = int(input("Nilai UTS  : "))
        nilai_uas = int(input("Nilai UAS  : "))

        daftar_nilai = [nilai_tugas, nilai_uts, nilai_uas]

        for nilai in daftar_nilai:
            if nilai < 0 or nilai > 100:
                print("\nNilai harus berada antara 0 sampai 100!")
                return

        cur.execute("""
            INSERT INTO nilai_akademik
            (
                semester,
                tahun_ajaran,
                nilai_tugas,
                nilai_uts,
                nilai_uas,
                id_siswa,
                id_guru
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            semester,
            tahun_ajaran,
            nilai_tugas,
            nilai_uts,
            nilai_uas,
            id_siswa,
            id_guru
        ))

        conn.commit()

        nilai_akhir = sum(daftar_nilai) / 3

        print("\nNilai akademik berhasil ditambahkan!")
        print(f"Nilai Akhir: {nilai_akhir:.2f}")

    except ValueError:
        conn.rollback()
        print("\nNilai harus berupa angka!")

    except Exception as error:
        conn.rollback()
        print("Gagal menambahkan nilai:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 3. MENGUBAH NILAI AKADEMIK
# ==================================
def ubah_nilai_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_nilai_guru(id_guru)

        id_nilai = input("\nMasukkan ID Nilai yang ingin diubah: ")

        cur.execute("""
            SELECT
                semester,
                tahun_ajaran,
                nilai_tugas,
                nilai_uts,
                nilai_uas
            FROM nilai_akademik
            WHERE id_nilai_akademik = %s
              AND id_guru = %s
        """, (id_nilai, id_guru))

        data = cur.fetchone()

        if data is None:
            print("\nID Nilai tidak ditemukan!")
            return

        print("\n===== UBAH NILAI AKADEMIK =====")
        print("Kosongkan input jika tidak ingin mengubah.")

        semester = input(
            f"Semester [{data[0]}]: "
        ).capitalize()

        if semester == "":
            semester = data[0]

        if semester not in ["Ganjil", "Genap"]:
            print("\nSemester tidak valid!")
            return

        tahun_ajaran = input(
            f"Tahun Ajaran [{data[1]}]: "
        ) or data[1]

        if len(tahun_ajaran) > 10:
            print("\nTahun ajaran terlalu panjang!")
            return

        nilai_tugas = input(
            f"Nilai Tugas [{data[2]}]: "
        )

        nilai_uts = input(
            f"Nilai UTS [{data[3]}]: "
        )

        nilai_uas = input(
            f"Nilai UAS [{data[4]}]: "
        )

        nilai_tugas = int(nilai_tugas) if nilai_tugas else data[2]
        nilai_uts = int(nilai_uts) if nilai_uts else data[3]
        nilai_uas = int(nilai_uas) if nilai_uas else data[4]

        daftar_nilai = [nilai_tugas, nilai_uts, nilai_uas]

        for nilai in daftar_nilai:
            if nilai < 0 or nilai > 100:
                print("\nNilai harus antara 0 sampai 100!")
                return

        cur.execute("""
            UPDATE nilai_akademik
            SET semester = %s,
                tahun_ajaran = %s,
                nilai_tugas = %s,
                nilai_uts = %s,
                nilai_uas = %s
            WHERE id_nilai_akademik = %s
              AND id_guru = %s
        """, (
            semester,
            tahun_ajaran,
            nilai_tugas,
            nilai_uts,
            nilai_uas,
            id_nilai,
            id_guru
        ))

        conn.commit()

        print("\nNilai akademik berhasil diubah!")

    except ValueError:
        conn.rollback()
        print("\nInput nilai harus berupa angka!")

    except Exception as error:
        conn.rollback()
        print("Gagal mengubah nilai:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 4. MENGHAPUS NILAI AKADEMIK
# ==================================
def hapus_nilai_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_nilai_guru(id_guru)

        id_nilai = input("\nMasukkan ID Nilai yang ingin dihapus: ")

        cur.execute("""
            SELECT s.nama_siswa
            FROM nilai_akademik n
            JOIN siswa s
                ON n.id_siswa = s.id_siswa
            WHERE n.id_nilai_akademik = %s
              AND n.id_guru = %s
        """, (id_nilai, id_guru))

        data = cur.fetchone()

        if data is None:
            print("\nID Nilai tidak ditemukan!")
            return

        print("\nNama Siswa:", data[0])

        konfirmasi = input(
            "Yakin ingin menghapus nilai ini? (y/n): "
        )

        if konfirmasi.lower() == "y":

            cur.execute("""
                DELETE FROM nilai_akademik
                WHERE id_nilai_akademik = %s
                  AND id_guru = %s
            """, (id_nilai, id_guru))

            conn.commit()

            print("\nNilai akademik berhasil dihapus!")

        else:
            print("\nPenghapusan dibatalkan.")

    except Exception as error:
        conn.rollback()
        print("Gagal menghapus nilai:", error)

    finally:
        cur.close()
        conn.close()







# ==================================
# 1. MENAMPILKAN PRESENSI GURU
# ==================================
def tampilkan_presensi_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                p.id_presensi,
                p.tanggal,
                s.nis,
                s.nama_siswa,
                k.nama_kelas,
                mp.nama_mapel,
                j.hari,
                p.status_kehadiran,
                p.keterangan
            FROM presensi p
            JOIN siswa s ON p.id_siswa = s.id_siswa
            JOIN kelas k ON s.id_kelas = k.id_kelas
            JOIN jadwal j ON p.id_jadwal = j.id_jadwal
            JOIN mata_pelajaran mp ON j.id_mapel = mp.id_mapel
            WHERE p.id_guru = %s
              AND mp.id_guru = %s
            ORDER BY p.tanggal DESC, s.nama_siswa
        """, (id_guru, id_guru))

        data = cur.fetchall()

        if data:
            kolom = [
                "ID Presensi",
                "Tanggal",
                "NIS",
                "Nama Siswa",
                "Kelas",
                "Mata Pelajaran",
                "Hari",
                "Status",
                "Keterangan"
            ]

            df = pd.DataFrame(data, columns=kolom)

            print("\n===== DATA PRESENSI SISWA =====")
            print(df.to_string(index=False))

        else:
            print("\nBelum ada data presensi.")

    except Exception as error:
        print("Gagal menampilkan presensi:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 2. MENAMBAH PRESENSI
# ==================================
def tambah_presensi_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        # Menampilkan jadwal guru
        query = """
            SELECT
                j.id_jadwal,
                j.hari,
                j.tanggal,
                j.jam_mulai,
                j.jam_selesai,
                k.nama_kelas,
                mp.nama_mapel,
                j.id_kelas
            FROM jadwal j
            JOIN kelas k
                ON j.id_kelas = k.id_kelas
            JOIN mata_pelajaran mp
                ON j.id_mapel = mp.id_mapel
            WHERE mp.id_guru = %s
            ORDER BY j.tanggal, j.jam_mulai
        """

        cur.execute(query, (id_guru,))
        jadwal = cur.fetchall()

        if not jadwal:
            print("Tidak ada jadwal mengajar.")
            return

        print("\n===== DAFTAR JADWAL =====")

        df = pd.DataFrame(
            jadwal,
            columns=[
                "ID Jadwal",
                "Hari",
                "Tanggal",
                "Jam Mulai",
                "Jam Selesai",
                "Kelas",
                "Mata Pelajaran",
                "ID Kelas"
            ]
        )

        print(df.to_string(index=False))

        id_jadwal = int(input("\nMasukkan ID Jadwal: "))

        # Mengambil kelas dan tanggal jadwal
        cur.execute("""
            SELECT j.id_kelas, j.tanggal
            FROM jadwal j
            JOIN mata_pelajaran mp ON j.id_mapel = mp.id_mapel
            WHERE j.id_jadwal = %s
              AND mp.id_guru = %s
        """, (id_jadwal, id_guru))

        data_jadwal = cur.fetchone()

        if data_jadwal is None:
            print("Jadwal tidak ditemukan.")
            return

        id_kelas, tanggal_jadwal = data_jadwal

        # Mengambil seluruh siswa dalam kelas
        cur.execute("""
            SELECT id_siswa, nis, nama_siswa
            FROM siswa
            WHERE id_kelas = %s
            ORDER BY id_siswa
        """, (id_kelas,))

        siswa = cur.fetchall()

        if not siswa:
            print("Tidak ada siswa dalam kelas ini.")
            return

        print("\n===== INPUT PRESENSI =====")

        total_hadir = 0
        total_izin = 0
        total_sakit = 0
        total_alpa = 0

        for nomor, data in enumerate(siswa, start=1):

            id_siswa, nis, nama = data

            print("\n" + "=" * 35)
            print(f"SISWA {nomor} DARI {len(siswa)}")
            print("=" * 35)

            print(f"NIS  : {nis}")
            print(f"Nama : {nama}")

            # Input status presensi
            while True:
                print("\nPilih Status:")
                print("1. Hadir")
                print("2. Izin")
                print("3. Sakit")
                print("4. Alpa")

                pilihan = input("Pilih status: ")

                match pilihan:
                    case "1":
                        status = "Hadir"
                        total_hadir += 1
                        break

                    case "2":
                        status = "Izin"
                        total_izin += 1
                        break

                    case "3":
                        status = "Sakit"
                        total_sakit += 1
                        break

                    case "4":
                        status = "Alpa"
                        total_alpa += 1
                        break

                    case _:
                        print("Pilihan tidak valid!")

            keterangan = input("Keterangan (boleh kosong): ")

            # Menyimpan presensi
            cur.execute("""
                INSERT INTO presensi (
                    tanggal,
                    status_kehadiran,
                    keterangan,
                    id_guru,
                    id_siswa,
                    id_jadwal
                )
                VALUES (%s, %s, %s, %s, %s, %s)

                ON CONFLICT (id_siswa, id_jadwal, tanggal)
                DO UPDATE SET
                    status_kehadiran = EXCLUDED.status_kehadiran,
                    keterangan = EXCLUDED.keterangan
            """, (
                tanggal_jadwal,
                status,
                keterangan,
                id_guru,
                id_siswa,
                id_jadwal
            ))

            print(f"\nPresensi {nama} berhasil disimpan!")

        # Menyimpan seluruh perubahan
        conn.commit()

        print("\n" + "=" * 35)
        print("       REKAP PRESENSI")
        print("=" * 35)

        print(f"Total Siswa : {len(siswa)}")
        print(f"Hadir       : {total_hadir}")
        print(f"Izin        : {total_izin}")
        print(f"Sakit       : {total_sakit}")
        print(f"Alpa        : {total_alpa}")

        print("=" * 35)
        print("Seluruh presensi berhasil disimpan!")

    except Exception as e:
        conn.rollback()
        print("Terjadi kesalahan:", e)

    finally:
        cur.close()
        conn.close()

# ==================================
# 3. MENGUBAH PRESENSI
# ==================================
def ubah_presensi_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_presensi_guru(id_guru)

        id_presensi = input("\nMasukkan ID Presensi: ")

        cur.execute("""
            SELECT
                p.tanggal,
                p.status_kehadiran,
                p.keterangan
            FROM presensi p
            JOIN jadwal j ON p.id_jadwal = j.id_jadwal
            JOIN mata_pelajaran mp ON j.id_mapel = mp.id_mapel
            WHERE p.id_presensi = %s
              AND p.id_guru = %s
              AND mp.id_guru = %s
        """, (id_presensi, id_guru, id_guru))

        data = cur.fetchone()

        if data is None:
            print("\nID Presensi tidak ditemukan!")
            return

        print("\n===== UBAH DATA PRESENSI =====")
        print("Kosongkan input jika tidak ingin mengubah.")

        tanggal = input(
            f"Tanggal [{data[0]}]: "
        ) or data[0]

        print("\nPilihan Status:")
        print("1. Hadir")
        print("2. Izin")
        print("3. Sakit")
        print("4. Alpa")

        print("Status sekarang:", data[1])
        pilihan = input("Pilih status baru (kosong = tetap): ")

        status = {
            "1": "Hadir",
            "2": "Izin",
            "3": "Sakit",
            "4": "Alpa"
        }

        if pilihan == "":
            status_baru = data[1]
        elif pilihan in status:
            status_baru = status[pilihan]
        else:
            print("\nPilihan status tidak valid!")
            return

        keterangan = input(
            f"Keterangan [{data[2] or ''}]: "
        )

        if keterangan == "":
            keterangan = data[2]

        cur.execute("""
            UPDATE presensi
            SET tanggal = %s,
                status_kehadiran = %s,
                keterangan = %s
            WHERE id_presensi = %s
              AND id_guru = %s
        """, (
            tanggal,
            status_baru,
            keterangan,
            id_presensi,
            id_guru
        ))

        conn.commit()
        print("\nData presensi berhasil diubah!")

    except Exception as error:
        conn.rollback()
        print("Gagal mengubah presensi:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# 4. MENGHAPUS PRESENSI
# ==================================
def hapus_presensi_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_presensi_guru(id_guru)

        id_presensi = input("\nMasukkan ID Presensi: ")

        cur.execute("""
            SELECT p.id_presensi, s.nama_siswa
            FROM presensi p
            JOIN siswa s ON p.id_siswa = s.id_siswa
            JOIN jadwal j ON p.id_jadwal = j.id_jadwal
            JOIN mata_pelajaran mp ON j.id_mapel = mp.id_mapel
            WHERE p.id_presensi = %s
              AND p.id_guru = %s
              AND mp.id_guru = %s
        """, (id_presensi, id_guru, id_guru))

        data = cur.fetchone()

        if data is None:
            print("\nID Presensi tidak ditemukan!")
            return

        print("\nNama Siswa:", data[1])

        konfirmasi = input(
            "Yakin ingin menghapus presensi ini? (y/n): "
        )

        if konfirmasi.lower() == "y":
            cur.execute("""
                DELETE FROM presensi
                WHERE id_presensi = %s
                  AND id_guru = %s
            """, (id_presensi, id_guru))

            conn.commit()
            print("\nPresensi berhasil dihapus!")

        else:
            print("\nPenghapusan dibatalkan.")

    except Exception as error:
        conn.rollback()
        print("Gagal menghapus presensi:", error)

    finally:
        cur.close()
        conn.close()




# ==================================
# 1. READ - MENAMPILKAN DATA SISWA
# ==================================

def tampilkan_siswa():

    conn, cur = connectDB()

    if conn is None:
        return

    cur.execute("""
        SELECT
            s.id_siswa,
            s.nis,
            s.nama_siswa,
            s.tanggal_lahir,
            s.jenis_kelamin,
            w.nama_wali_murid,
            k.nama_kelas,
            a.nama_wilayah
        FROM siswa s
        JOIN wali_murid w
            ON s.id_wali_murid = w.id_wali_murid
        JOIN kelas k
            ON s.id_kelas = k.id_kelas
        JOIN alamat a
            ON s.id_alamat = a.id_alamat
        ORDER BY s.id_siswa
    """)

    data = cur.fetchall()

    if data:

        kolom = [
            "ID",
            "NIS",
            "Nama Siswa",
            "Tanggal Lahir",
            "Jenis Kelamin",
            "Wali Murid",
            "Kelas",
            "Alamat"
        ]

        df = pd.DataFrame(data, columns=kolom)

        print("\n===== DATA SISWA =====")
        print(df.to_string(index=False))

    else:
        print("\nData Siswa masih kosong.")

    cur.close()
    conn.close()

# ==================================
# 2. CREATE - MENAMBAH DATA SISWA
# ==================================

def tambah_siswa():

    conn, cur = connectDB()

    if conn is None:
        return

    print("\n===== TAMBAH DATA SISWA =====")

    try:

        # Menampilkan wali murid
        cur.execute("""
            SELECT id_wali_murid, nama_wali_murid
            FROM wali_murid
            ORDER BY id_wali_murid
        """)

        print("\n===== DAFTAR WALI MURID =====")

        for w in cur.fetchall():
            print(w[0], "-", w[1])

        # Menampilkan kelas
        cur.execute("""
            SELECT id_kelas, nama_kelas
            FROM kelas
            ORDER BY id_kelas
        """)

        print("\n===== DAFTAR KELAS =====")

        for k in cur.fetchall():
            print(k[0], "-", k[1])

        # Menampilkan alamat
        cur.execute("""
            SELECT id_alamat, nama_wilayah
            FROM alamat
            ORDER BY id_alamat
        """)

        print("\n===== DAFTAR ALAMAT =====")

        for a in cur.fetchall():
            print(a[0], "-", a[1])

        # Input data siswa
        nis = input("\nNIS             : ")
        nama = input("Nama Siswa      : ")
        tanggal = input("Tanggal Lahir (YYYY-MM-DD): ")
        jk = input("Jenis Kelamin (L/P): ").upper()
        id_wali = input("ID Wali Murid   : ")
        id_kelas = input("ID Kelas        : ")
        id_alamat = input("ID Alamat       : ")

        cur.execute("""
            INSERT INTO siswa
            (nis, nama_siswa, tanggal_lahir,
             jenis_kelamin, id_wali_murid,
             id_kelas, id_alamat)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            nis, nama, tanggal, jk,
            id_wali, id_kelas, id_alamat
        ))

        conn.commit()

        print("\nData Siswa berhasil ditambahkan!")

    except Exception as error:

        conn.rollback()
        print("\nGagal menambahkan data:", error)

    cur.close()
    conn.close()

# ==================================
# 3. UPDATE - MENGUBAH DATA SISWA
# ==================================

def ubah_siswa():

    conn, cur = connectDB()

    if conn is None:
        return

    print("\n===== UBAH DATA SISWA =====")

    id_siswa = input("Masukkan ID Siswa: ")

    cur.execute("""
        SELECT *
        FROM siswa
        WHERE id_siswa = %s
    """, (id_siswa,))

    data = cur.fetchone()

    if data:

        print("\nData ditemukan!")
        print("Nama Siswa:", data[2])

        try:

            # Menampilkan pilihan wali murid
            cur.execute("""
                SELECT id_wali_murid, nama_wali_murid
                FROM wali_murid
                ORDER BY id_wali_murid
            """)

            print("\n===== DAFTAR WALI MURID =====")

            for w in cur.fetchall():
                print(w[0], "-", w[1])

            # Menampilkan pilihan kelas
            cur.execute("""
                SELECT id_kelas, nama_kelas
                FROM kelas
                ORDER BY id_kelas
            """)

            print("\n===== DAFTAR KELAS =====")

            for k in cur.fetchall():
                print(k[0], "-", k[1])

            # Menampilkan pilihan alamat
            cur.execute("""
                SELECT id_alamat, nama_wilayah
                FROM alamat
                ORDER BY id_alamat
            """)

            print("\n===== DAFTAR ALAMAT =====")

            for a in cur.fetchall():
                print(a[0], "-", a[1])

            nis = input("\nNIS             : ")
            nama = input("Nama Siswa      : ")
            tanggal = input("Tanggal Lahir (YYYY-MM-DD): ")
            jk = input("Jenis Kelamin (L/P): ").upper()
            id_wali = input("ID Wali Murid   : ")
            id_kelas = input("ID Kelas        : ")
            id_alamat = input("ID Alamat       : ")

            cur.execute("""
                UPDATE siswa
                SET nis = %s,
                    nama_siswa = %s,
                    tanggal_lahir = %s,
                    jenis_kelamin = %s,
                    id_wali_murid = %s,
                    id_kelas = %s,
                    id_alamat = %s
                WHERE id_siswa = %s
            """, (
                nis, nama, tanggal, jk,
                id_wali, id_kelas, id_alamat,
                id_siswa
            ))

            conn.commit()

            print("\nData Siswa berhasil diubah!")

        except Exception as error:

            conn.rollback()
            print("\nGagal mengubah data:", error)

    else:
        print("\nID Siswa tidak ditemukan!")

    cur.close()
    conn.close()

# ==================================
# 4. DELETE - MENGHAPUS DATA SISWA
# ==================================

def hapus_siswa():

    conn, cur = connectDB()

    if conn is None:
        return

    print("\n===== HAPUS DATA SISWA =====")

    id_siswa = input("Masukkan ID Siswa: ")

    cur.execute("""
        SELECT nama_siswa
        FROM siswa
        WHERE id_siswa = %s
    """, (id_siswa,))

    data = cur.fetchone()

    if data:

        print("\nData ditemukan!")
        print("Nama Siswa:", data[0])

        konfirmasi = input(
            "\nYakin ingin menghapus data ini? (y/n): "
        )

        match konfirmasi.lower():

            case "y":

                try:

                    cur.execute("""
                        DELETE FROM siswa
                        WHERE id_siswa = %s
                    """, (id_siswa,))

                    conn.commit()

                    print("\nData Siswa berhasil dihapus!")

                except Exception as error:

                    conn.rollback()
                    print("\nGagal menghapus data:", error)

            case "n":
                print("\nPenghapusan dibatalkan!")

            case _:
                print("\nPilihan tidak tersedia!")

    else:
        print("\nID Siswa tidak ditemukan!")

    cur.close()
    conn.close()

def lihat_siswa_wali(id_wali):

    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                s.id_siswa,
                s.nis,
                s.nama_siswa,
                s.tanggal_lahir,
                s.jenis_kelamin,
                k.nama_kelas,
                a.nama_wilayah
            FROM siswa s
            JOIN kelas k
                ON s.id_kelas = k.id_kelas
            JOIN alamat a
                ON s.id_alamat = a.id_alamat
            WHERE s.id_wali_murid = %s
            ORDER BY s.nama_siswa
        """, (id_wali,))

        data = cur.fetchall()

        if data:

            print("\n================================")
            print("       DATA SISWA ANDA")
            print("================================")

            for siswa in data:

                print("\nID Siswa      :", siswa[0])
                print("NIS           :", siswa[1])
                print("Nama          :", siswa[2])
                print("Tanggal Lahir :", siswa[3])
                print("Jenis Kelamin :", siswa[4])
                print("Kelas         :", siswa[5])
                print("Alamat        :", siswa[6])
                print("--------------------------------")

        else:
            print("\nAnda belum memiliki data siswa.")

    except Exception as error:
        print("Terjadi kesalahan:", error)

    finally:
        cur.close()
        conn.close()

# ==================================
# MELIHAT DATA SISWA BERDASARKAN GURU
# ==================================
def lihat_siswa_guru(id_guru):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        query = """
            SELECT DISTINCT
                s.id_siswa,
                s.nis,
                s.nama_siswa,
                s.tanggal_lahir,
                s.jenis_kelamin,
                k.nama_kelas,
                w.nama_wali_murid
            FROM siswa s
            JOIN kelas k
                ON s.id_kelas = k.id_kelas
            JOIN wali_murid w
                ON s.id_wali_murid = w.id_wali_murid
            JOIN jadwal j
                ON s.id_kelas = j.id_kelas
            JOIN mata_pelajaran mp
                ON j.id_mapel = mp.id_mapel
            WHERE mp.id_guru = %s
            ORDER BY k.nama_kelas, s.nama_siswa
        """

        cur.execute(query, (id_guru,))
        data = cur.fetchall()

        if data:
            kolom = [
                "ID Siswa",
                "NIS",
                "Nama Siswa",
                "Tanggal Lahir",
                "Jenis Kelamin",
                "Kelas",
                "Nama Wali Murid"
            ]

            df = pd.DataFrame(data, columns=kolom)

            print("\n===== DATA SISWA YANG DIAJAR =====")
            print(df.to_string(index=False))

        else:
            print("\nBelum ada siswa yang diajar oleh Guru ini.")

    except Exception as error:
        print("Gagal menampilkan data siswa:", error)

    finally:
        cur.close()
        conn.close()




def tampilkan_staf():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        query = """
            SELECT
                s.id_staf,
                s.nama_staf,
                s.jabatan,
                s.no_telepon,
                s.username,
                a.nama_wilayah
            FROM staf s
            JOIN alamat a
                ON s.id_alamat = a.id_alamat
            ORDER BY s.id_staf
        """

        cur.execute(query)
        data = cur.fetchall()

        if not data:
            print("Data staf belum tersedia.")
            return

        kolom = [
            "ID Staf",
            "Nama Staf",
            "Jabatan",
            "No Telepon",
            "Username",
            "Alamat"
        ]

        df = pd.DataFrame(data, columns=kolom)

        print("\n===== DATA STAF =====")
        print(df.to_string(index=False))

    except Exception as error:
        print("Gagal menampilkan data staf:", error)

    finally:
        cur.close()
        conn.close()

def tampilkan_alamat(cur):
    cur.execute("""
        SELECT id_alamat, nama_wilayah
        FROM alamat
        ORDER BY id_alamat
    """)

    data = cur.fetchall()

    if not data:
        print("Data alamat belum tersedia.")
        return False

    print("\n===== DATA ALAMAT =====")

    for alamat in data:
        print(f"ID: {alamat[0]} | Wilayah: {alamat[1]}")

    return True

def tambah_staf():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        nama = input("Nama Staf: ")
        jabatan = input("Jabatan: ")
        telepon = input("Nomor Telepon: ")
        username = input("Username: ")
        password = input("Password: ")

        if not tampilkan_alamat(cur):
            return

        id_alamat = int(input("\nMasukkan ID Alamat: "))

        query = """
            INSERT INTO staf
            (nama_staf, jabatan, no_telepon,
             username, password, id_alamat)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cur.execute(query, (
            nama,
            jabatan,
            telepon,
            username,
            password,
            id_alamat
        ))

        conn.commit()
        print("Data staf berhasil ditambahkan!")

    except ValueError:
        conn.rollback()
        print("ID alamat harus berupa angka!")

    except Exception as error:
        conn.rollback()
        print("Gagal menambahkan staf:", error)

    finally:
        cur.close()
        conn.close()

def ubah_staf():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_staf()

        id_staf = int(input("\nMasukkan ID Staf yang ingin diubah: "))

        cur.execute("""
            SELECT *
            FROM staf
            WHERE id_staf = %s
        """, (id_staf,))

        data = cur.fetchone()

        if data is None:
            print("Data staf tidak ditemukan!")
            return

        print("\n===== UBAH DATA STAF =====")

        nama = input("Nama Staf Baru: ")
        jabatan = input("Jabatan Baru: ")
        telepon = input("Nomor Telepon Baru: ")
        username = input("Username Baru: ")
        password = input("Password Baru: ")

        if not tampilkan_alamat(cur):
            return

        id_alamat = int(input("\nMasukkan ID Alamat Baru: "))

        query = """
            UPDATE staf
            SET nama_staf = %s,
                jabatan = %s,
                no_telepon = %s,
                username = %s,
                password = %s,
                id_alamat = %s
            WHERE id_staf = %s
        """

        cur.execute(query, (
            nama,
            jabatan,
            telepon,
            username,
            password,
            id_alamat,
            id_staf
        ))

        conn.commit()
        print("Data staf berhasil diubah!")

    except ValueError:
        conn.rollback()
        print("ID harus berupa angka!")

    except Exception as error:
        conn.rollback()
        print("Gagal mengubah data staf:", error)

    finally:
        cur.close()
        conn.close()

def hapus_staf():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_staf()

        id_staf = int(input("\nMasukkan ID Staf yang ingin dihapus: "))

        cur.execute("""
            SELECT id_staf
            FROM staf
            WHERE id_staf = %s
        """, (id_staf,))

        if cur.fetchone() is None:
            print("Data staf tidak ditemukan!")
            return

        konfirmasi = input(
            "Yakin ingin menghapus data staf? (y/n): "
        ).lower()

        if konfirmasi == "y":
            cur.execute("""
                DELETE FROM staf
                WHERE id_staf = %s
            """, (id_staf,))

            conn.commit()
            print("Data staf berhasil dihapus!")

        else:
            print("Penghapusan dibatalkan.")

    except ValueError:
        conn.rollback()
        print("ID staf harus berupa angka!")

    except Exception as error:
        conn.rollback()
        print("Gagal menghapus data staf:", error)

    finally:
        cur.close()
        conn.close()




# ==========================================
# MENAMBAH TAGIHAN SPP
# ==========================================

def tambah_tagihan():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        # 1. Menampilkan daftar siswa
        cur.execute("""
            SELECT
                s.id_siswa,
                s.nama_siswa,
                w.nama_wali_murid
            FROM siswa s
            JOIN wali_murid w
                ON s.id_wali_murid = w.id_wali_murid
            ORDER BY s.id_siswa
        """)

        data = cur.fetchall()

        if not data:
            print("\nBelum ada data siswa.")
            return

        kolom = [
            "ID Siswa",
            "Nama Siswa",
            "Nama Wali Murid"
        ]

        df = pd.DataFrame(data, columns=kolom)

        print("\n===== DAFTAR SISWA =====")
        print(df.to_string(index=False))

        # 2. Memilih siswa
        id_siswa = int(input("\nMasukkan ID Siswa: "))

        cur.execute("""
            SELECT id_siswa
            FROM siswa
            WHERE id_siswa = %s
        """, (id_siswa,))

        if cur.fetchone() is None:
            print("Siswa tidak ditemukan!")
            return

        # 3. Memasukkan bulan
        bulan = input(
            "Masukkan Bulan Tagihan: "
        ).strip().capitalize()

        daftar_bulan = [
            "Januari", "Februari", "Maret",
            "April", "Mei", "Juni",
            "Juli", "Agustus", "September",
            "Oktober", "November", "Desember"
        ]

        if bulan not in daftar_bulan:
            print("Nama bulan tidak valid!")
            return

        # 4. Memasukkan tahun
        tahun = int(input("Masukkan Tahun: "))

        if tahun < 2000 or tahun > 2100:
            print("Tahun tidak valid!")
            return

        # 5. Memasukkan nominal
        nominal = int(input("Masukkan Nominal SPP: Rp"))

        if nominal <= 0:
            print("Nominal harus lebih dari 0!")
            return

        # 6. Menyimpan tagihan
        cur.execute("""
            INSERT INTO tagihan_spp
            (bulan, tahun, nominal, id_siswa)
            VALUES (%s, %s, %s, %s)
        """, (bulan, tahun, nominal, id_siswa))

        conn.commit()

        print("\nTagihan SPP berhasil ditambahkan!")
        print("Nama Bulan :", bulan)
        print("Tahun      :", tahun)
        print("Nominal    : Rp", nominal)
        print("Status     : Belum Lunas")

    except ValueError:
        conn.rollback()
        print("Input angka tidak valid!")

    except Exception as error:
        conn.rollback()
        print("Gagal menambahkan tagihan:", error)

    finally:
        cur.close()
        conn.close()

# ==========================================
# MENAMPILKAN SEMUA TAGIHAN (STAF)
# ==========================================

def tampilkan_tagihan():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        query = """
            SELECT
                t.id_tagihan,
                t.bulan,
                t.tahun,
                s.nama_siswa,
                w.nama_wali_murid,
                t.nominal,
                t.status_pembayaran
            FROM tagihan_spp t
            JOIN siswa s
                ON t.id_siswa = s.id_siswa
            JOIN wali_murid w
                ON s.id_wali_murid = w.id_wali_murid
            ORDER BY t.tahun, t.id_tagihan
        """

        cur.execute(query)
        data = cur.fetchall()

        if not data:
            print("\nBelum ada data tagihan SPP.")
            return

        kolom = [
            "ID Tagihan",
            "Bulan",
            "Tahun",
            "Nama Siswa",
            "Nama Wali",
            "Nominal",
            "Status Pembayaran"
        ]

        df = pd.DataFrame(data, columns=kolom)

        print("\n===== DATA TAGIHAN SPP =====")
        print(df.to_string(index=False))

    except Exception as error:
        print("Gagal menampilkan tagihan:", error)

    finally:
        cur.close()
        conn.close()

# ==========================================
# MENAMPILKAN TAGIHAN MILIK WALI MURID
# ==========================================

def tampilkan_tagihan_wali(id_wali):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        query = """
            SELECT
                t.id_tagihan,
                t.bulan,
                t.tahun,
                s.nama_siswa,
                t.nominal,
                t.status_pembayaran
            FROM tagihan_spp t
            JOIN siswa s
                ON t.id_siswa = s.id_siswa
            WHERE s.id_wali_murid = %s
            ORDER BY t.tahun, t.id_tagihan
        """

        cur.execute(query, (id_wali,))
        data = cur.fetchall()

        if not data:
            print("\nBelum ada tagihan SPP.")
            return

        kolom = [
            "ID Tagihan",
            "Bulan",
            "Tahun",
            "Nama Siswa",
            "Nominal",
            "Status Pembayaran"
        ]

        df = pd.DataFrame(data, columns=kolom)

        print("\n===== TAGIHAN SPP =====")
        print(df.to_string(index=False))

    except Exception as error:
        print("Gagal menampilkan tagihan:", error)

    finally:
        cur.close()
        conn.close()




# ==========================================
# MENAMPILKAN SEMUA TRANSAKSI
# ==========================================

def tampilkan_transaksi():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        query = """
            SELECT
                t.id_transaksi,
                t.id_tagihan,
                t.tanggal_pembayaran,
                t.metode_pembayaran,
                t.nominal,
                t.id_staf,
                w.nama_wali_murid,
                s.nama_siswa
            FROM transaksi t
            JOIN wali_murid w
                ON t.id_wali_murid = w.id_wali_murid
            JOIN siswa s
                ON t.id_siswa = s.id_siswa
            ORDER BY t.id_transaksi
        """

        cur.execute(query)
        data = cur.fetchall()

        if not data:
            print("Belum ada data transaksi SPP.")
            return

        kolom = [
            "ID Transaksi",
            "ID Tagihan",
            "Tanggal Pembayaran",
            "Metode",
            "Nominal",
            "ID Staf",
            "Nama Wali Murid",
            "Nama Siswa"
        ]

        df = pd.DataFrame(data, columns=kolom)

        print("\n===== DATA TRANSAKSI SPP =====")
        print(df.to_string(index=False))

    except Exception as error:
        print("Gagal menampilkan transaksi:", error)

    finally:
        cur.close()
        conn.close()

# ==========================================
# MENAMPILKAN DATA WALI DAN SISWA
# ==========================================

def tampilkan_wali_siswa(cur):
    print("\n===== DATA WALI MURID =====")

    cur.execute("""
        SELECT id_wali_murid, nama_wali_murid
        FROM wali_murid
        ORDER BY id_wali_murid
    """)

    data_wali = cur.fetchall()

    if not data_wali:
        print("Data wali murid belum tersedia.")
        return False

    for data in data_wali:
        print(f"ID: {data[0]} | Nama: {data[1]}")

    print("\n===== DATA SISWA =====")

    cur.execute("""
        SELECT id_siswa, nama_siswa, id_wali_murid
        FROM siswa
        ORDER BY id_siswa
    """)

    data_siswa = cur.fetchall()

    if not data_siswa:
        print("Data siswa belum tersedia.")
        return False

    for data in data_siswa:
        print(
            f"ID: {data[0]} | Nama: {data[1]} "
            f"| ID Wali: {data[2]}"
        )

    return True

# ==========================================
# MENAMBAHKAN TRANSAKSI PEMBAYARAN
# ==========================================

def tambah_transaksi(id_staf):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        # 1. Menampilkan tagihan yang belum lunas
        query = """
            SELECT
                t.id_tagihan,
                t.bulan,
                t.tahun,
                s.nama_siswa,
                w.nama_wali_murid,
                t.nominal
            FROM tagihan_spp t
            JOIN siswa s
                ON t.id_siswa = s.id_siswa
            JOIN wali_murid w
                ON s.id_wali_murid = w.id_wali_murid
            WHERE t.status_pembayaran = 'Belum Lunas'
            ORDER BY t.id_tagihan
        """

        cur.execute(query)
        data = cur.fetchall()

        if not data:
            print("\nTidak ada tagihan yang belum lunas.")
            return

        kolom = [
            "ID Tagihan",
            "Bulan",
            "Tahun",
            "Nama Siswa",
            "Nama Wali",
            "Nominal"
        ]

        df = pd.DataFrame(data, columns=kolom)

        print("\n===== DAFTAR TAGIHAN BELUM LUNAS =====")
        print(df.to_string(index=False))

        # 2. Memilih tagihan
        id_tagihan = int(
            input("\nMasukkan ID Tagihan yang dibayar: ")
        )

        # Mengambil dan mengunci tagihan
        cur.execute("""
            SELECT
                t.id_tagihan,
                t.nominal,
                t.status_pembayaran,
                s.id_siswa,
                s.id_wali_murid
            FROM tagihan_spp t
            JOIN siswa s
                ON t.id_siswa = s.id_siswa
            WHERE t.id_tagihan = %s
            FOR UPDATE OF t
        """, (id_tagihan,))

        tagihan = cur.fetchone()

        if tagihan is None:
            print("Tagihan tidak ditemukan!")
            return

        id_tagihan, nominal, status, id_siswa, id_wali = tagihan

        if status != "Belum Lunas":
            print("Tagihan ini sudah lunas!")
            return

        # 3. Memasukkan metode pembayaran
        metode = input(
            "Metode Pembayaran (Online/Offline): "
        ).strip().capitalize()

        if metode not in ["Online", "Offline"]:
            print("Metode pembayaran tidak valid!")
            return

        # 4. Memasukkan tanggal pembayaran
        tanggal = input(
            "Tanggal Pembayaran (YYYY-MM-DD HH:MM:SS) "
            "[Enter = sekarang]: "
        ).strip()

        if tanggal == "":
            tanggal = datetime.now()
        else:
            tanggal = datetime.strptime(
                tanggal, "%Y-%m-%d %H:%M:%S"
            )

        # 5. Menyimpan transaksi
        cur.execute("""
            INSERT INTO transaksi
            (
                tanggal_pembayaran,
                metode_pembayaran,
                nominal,
                id_staf,
                id_wali_murid,
                id_siswa,
                id_tagihan
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            tanggal,
            metode,
            nominal,
            id_staf,
            id_wali,
            id_siswa,
            id_tagihan
        ))

        # 6. Mengubah status tagihan
        cur.execute("""
            UPDATE tagihan_spp
            SET status_pembayaran = 'Lunas'
            WHERE id_tagihan = %s
        """, (id_tagihan,))

        conn.commit()

        print("\nPembayaran berhasil dicatat!")
        print("ID Tagihan :", id_tagihan)
        print("Nominal    : Rp", nominal)
        print("Status     : Lunas")

    except ValueError:
        conn.rollback()
        print("Input angka atau tanggal tidak valid!")

    except Exception as error:
        conn.rollback()
        print("Gagal menambahkan transaksi:", error)

    finally:
        cur.close()
        conn.close()

# ==========================================
# MENGUBAH DATA TRANSAKSI
# ==========================================

def ubah_transaksi():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_transaksi()

        id_transaksi = int(
            input("\nMasukkan ID Transaksi yang ingin diubah: ")
        )

        cur.execute("""
            SELECT id_transaksi
            FROM transaksi
            WHERE id_transaksi = %s
        """, (id_transaksi,))

        if cur.fetchone() is None:
            print("Transaksi tidak ditemukan!")
            return

        print("\nMasukkan data transaksi yang baru.")

        tanggal = input(
            "Tanggal Pembayaran (YYYY-MM-DD HH:MM:SS): "
        ).strip()

        tanggal = datetime.strptime(
            tanggal, "%Y-%m-%d %H:%M:%S"
        )

        metode = input(
            "Metode Pembayaran (Online/Offline): "
        ).strip().capitalize()

        if metode not in ["Online", "Offline"]:
            print("Metode pembayaran tidak valid!")
            return

        # Hanya tanggal dan metode yang dapat diubah.
        # Nominal dan hubungan tagihan tidak diubah.

        cur.execute("""
            UPDATE transaksi
            SET tanggal_pembayaran = %s,
                metode_pembayaran = %s
            WHERE id_transaksi = %s
        """, (
            tanggal,
            metode,
            id_transaksi
        ))

        conn.commit()
        print("Transaksi berhasil diubah!")

    except ValueError:
        conn.rollback()
        print("Input ID atau tanggal tidak valid!")

    except Exception as error:
        conn.rollback()
        print("Gagal mengubah transaksi:", error)

    finally:
        cur.close()
        conn.close()

# ==========================================
# MENGHAPUS TRANSAKSI
# ==========================================

def hapus_transaksi():
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        tampilkan_transaksi()

        id_transaksi = int(
            input("\nMasukkan ID Transaksi yang ingin dihapus: ")
        )

        cur.execute("""
            SELECT id_tagihan
            FROM transaksi
            WHERE id_transaksi = %s
        """, (id_transaksi,))

        data = cur.fetchone()

        if data is None:
            print("Transaksi tidak ditemukan!")
            return

        id_tagihan = data[0]

        konfirmasi = input(
            "Yakin ingin menghapus transaksi? (y/n): "
        ).strip().lower()

        if konfirmasi == "y":

            # Mengembalikan status tagihan jika terhubung
            if id_tagihan is not None:
                cur.execute("""
                    UPDATE tagihan_spp
                    SET status_pembayaran = 'Belum Lunas'
                    WHERE id_tagihan = %s
                """, (id_tagihan,))

            cur.execute("""
                DELETE FROM transaksi
                WHERE id_transaksi = %s
            """, (id_transaksi,))

            conn.commit()
            print("Transaksi berhasil dihapus!")

            if id_tagihan is not None:
                print("Status tagihan dikembalikan menjadi Belum Lunas.")

        else:
            print("Penghapusan dibatalkan.")

    except ValueError:
        conn.rollback()
        print("ID transaksi harus berupa angka!")

    except Exception as error:
        conn.rollback()
        print("Gagal menghapus transaksi:", error)

    finally:
        cur.close()
        conn.close()

# ==========================================
# RIWAYAT TRANSAKSI WALI MURID
# ==========================================

def lihat_riwayat_transaksi_wali(id_wali):
    conn, cur = connectDB()

    if conn is None:
        return

    try:
        query = """
            SELECT
                t.id_transaksi,
                t.tanggal_pembayaran,
                t.metode_pembayaran,
                t.nominal,
                s.nama_siswa,
                t.id_staf
            FROM transaksi t
            JOIN siswa s
                ON t.id_siswa = s.id_siswa
            WHERE t.id_wali_murid = %s
            ORDER BY t.tanggal_pembayaran DESC
        """

        cur.execute(query, (id_wali,))
        data = cur.fetchall()

        if not data:
            print("\nBelum ada riwayat transaksi SPP.")
            return

        kolom = [
            "ID Transaksi",
            "Tanggal Pembayaran",
            "Metode",
            "Nominal",
            "Nama Siswa",
            "ID Staf"
        ]

        df = pd.DataFrame(data, columns=kolom)

        print("\n===== RIWAYAT TRANSAKSI SPP =====")
        print(df.to_string(index=False))

    except Exception as error:
        print("Gagal menampilkan riwayat transaksi:", error)

    finally:
        cur.close()
        conn.close()




def tampilkan_wali_murid():

    conn, cur = connectDB()

    if conn is None:
        return

    cur.execute("""
        SELECT
            id_wali_murid,
            nama_wali_murid,
            no_telepon,
            email,
            username,
            id_alamat
        FROM wali_murid
        ORDER BY id_wali_murid
    """)

    data = cur.fetchall()

    if data:
        kolom = [
            "ID",
            "Nama Wali Murid",
            "No Telepon",
            "Email",
            "Username",
            "ID Alamat"
        ]

        df = pd.DataFrame(data, columns=kolom)

        print("\n===== DATA WALI MURID =====")
        print(df.to_string(index=False))

    else:
        print("\nData Wali Murid masih kosong.")

    cur.close()
    conn.close()

def tambah_wali_murid():

    conn, cur = connectDB()

    if conn is None:
        return

    print("\n===== TAMBAH DATA WALI MURID =====")

    # Menampilkan daftar alamat
    cur.execute("""
        SELECT id_alamat, nama_wilayah, jenis_wilayah
        FROM alamat
        ORDER BY id_alamat
    """)

    alamat = cur.fetchall()

    print("\n===== DAFTAR ALAMAT =====")

    for a in alamat:
        print(a[0], "-", a[1], "-", a[2])

    # Input data wali murid
    nama = input("\nNama Wali Murid : ")
    telepon = input("No Telepon      : ")
    email = input("Email           : ")
    username = input("Username        : ")
    password = input("Password        : ")
    id_alamat = input("ID Alamat       : ")

    try:
        cur.execute("""
            INSERT INTO wali_murid
            (nama_wali_murid, no_telepon, email,
             username, password, id_alamat)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nama, telepon, email, username, password, id_alamat))

        conn.commit()

        print("\nData Wali Murid berhasil ditambahkan!")

    except Exception as error:
        conn.rollback()
        print("\nGagal menambahkan data:", error)

    cur.close()
    conn.close()

def ubah_wali_murid():

    conn, cur = connectDB()

    if conn is None:
        return

    print("\n===== UBAH DATA WALI MURID =====")

    id_wali = input("Masukkan ID Wali Murid: ")

    # Memeriksa apakah ID tersedia
    cur.execute("""
        SELECT * FROM wali_murid
        WHERE id_wali_murid = %s
    """, (id_wali,))

    data = cur.fetchone()

    if data:

        print("\nData ditemukan!")
        print("Nama:", data[1])

        print("\nMasukkan data baru:")

        nama = input("Nama Wali Murid : ")
        telepon = input("No Telepon      : ")
        email = input("Email           : ")
        username = input("Username        : ")
        password = input("Password        : ")
        id_alamat = input("ID Alamat       : ")

        try:
            cur.execute("""
                UPDATE wali_murid
                SET nama_wali_murid = %s,
                    no_telepon = %s,
                    email = %s,
                    username = %s,
                    password = %s,
                    id_alamat = %s
                WHERE id_wali_murid = %s
            """, (
                nama, telepon, email,
                username, password, id_alamat,
                id_wali
            ))

            conn.commit()

            print("\nData berhasil diubah!")

        except Exception as error:
            conn.rollback()
            print("\nGagal mengubah data:", error)

    else:
        print("\nID Wali Murid tidak ditemukan!")

    cur.close()
    conn.close()

def hapus_wali_murid():

    conn, cur = connectDB()

    if conn is None:
        return

    print("\n===== HAPUS DATA WALI MURID =====")

    id_wali = input("Masukkan ID Wali Murid: ")

    # Memeriksa data berdasarkan ID
    cur.execute("""
        SELECT nama_wali_murid
        FROM wali_murid
        WHERE id_wali_murid = %s
    """, (id_wali,))

    data = cur.fetchone()

    if data:

        print("\nData ditemukan!")
        print("Nama Wali Murid:", data[0])

        konfirmasi = input(
            "\nYakin ingin menghapus data ini? (y/n): "
        )

        match konfirmasi.lower():

            case "y":

                try:
                    cur.execute("""
                        DELETE FROM wali_murid
                        WHERE id_wali_murid = %s
                    """, (id_wali,))

                    conn.commit()

                    print("\nData berhasil dihapus!")

                except Exception as error:
                    conn.rollback()
                    print("\nGagal menghapus data:", error)

            case "n":
                print("\nPenghapusan dibatalkan!")

            case _:
                print("\nPilihan tidak tersedia!")

    else:
        print("\nID Wali Murid tidak ditemukan!")

    cur.close()
    conn.close()

def lihat_data_wali_murid(id_wali):

    conn, cur = connectDB()

    if conn is None:
        return

    try:
        cur.execute("""
            SELECT
                w.id_wali_murid,
                w.nama_wali_murid,
                w.no_telepon,
                w.email,
                w.username,
                a.nama_wilayah
            FROM wali_murid w
            JOIN alamat a
                ON w.id_alamat = a.id_alamat
            WHERE w.id_wali_murid = %s
        """, (id_wali,))

        data = cur.fetchone()

        if data:

            print("\n================================")
            print("       DATA WALI MURID")
            print("================================")

            print("ID Wali Murid :", data[0])
            print("Nama          :", data[1])
            print("No. Telepon   :", data[2])
            print("Email         :", data[3])
            print("Username      :", data[4])
            print("Alamat        :", data[5])

        else:
            print("\nData Wali Murid tidak ditemukan!")

    except Exception as error:
        print("Terjadi kesalahan:", error)

    finally:
        cur.close()
        conn.close()

# ==========================================
# PROGRAM UTAMA
# ==========================================


if __name__ == "__main__":
    main()
