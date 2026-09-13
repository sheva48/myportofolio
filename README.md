Nama: Sheva Aquila Mahardika
NPM : 2506622033
Kelas: A

TUGAS 01
PERTANYAAN REFLEKTIF

1. Ya, saya menggunakan elemen semantik HTML5 seperti <header>, <main>, <section>, dan <footer> secara ekstensif dalam perancangan struktur halaman portofolio ini Penggunaan elemen semantik memberikan kejelasan pada makna struktural kode, yang sangat esensial dalam pengembangan static web agar mudah diinterpretasikan oleh peramban, perangkat aksesibilitas , maupun developer lain. Hal ini juga mempermudah pengorganisasian konten secara modular dan meminimalisasi penggunaan elemen generik <div>, sehingga penulisan aturan pemformatan CSS menjadi lebih terarah pada komponen spesifik.

2. Tantangan utamanya adalah mengatur grid dua kolom di bagian hero (foto dan profil) agar tetap proporsional dan tidak berantakan saat dibuka di layar HP yang kecil. Untuk mengatasinya, saya menggunakan media query (@media (max-width: 768px)) untuk menyusun ulang posisi foto dan identitas ke atas secara vertikal, sementara teks detailnya diletakkan di bawahnya. Selain itu, penggunaan fungsi grid dengan minmax() membuat kartu skills bisa menyesuaikan ukuran layarnya secara otomatis dengan rapi.

3. Keterbatasan utama dari static web murni adalah kontennya yang statis dan kaku, di mana pembaruan informasinya tidak bisa dilakukan secara interaktif tanpa mengubah kodenya langsung secara manual. Selain itu, belum ada sistem penyimpanan data. Jika ada kesempatan untuk menambahkan fitur pada iterasi proyek selanjutnya, saya ingin sekali mengintegrasikan backend menggunakan Django dengan pola MVT dan database, sehingga data profil, daftar keahlian, atau pesan pengunjung bisa dikelola secara dinamis melalui halaman admin Django.


AI Disclosure
Untuk penggunaan ai saya terlebih karena sudah ada tutorial dan beberapa code yang di sediakan pada tutorial, strategi saya adalah mempermudah kalimat tutorial yang di berikan agar mempermudah saya dalam pengerjaan, pada saat pengerjaan AI yang saya gunakan yaitu gemini, memberikan saya step by step dengan nomor nomor yang jelas agar mempermudah dan mempercepat pengerjaan. Kemudian untuk pengerjaan tugas individual 1 saya berdiskusi mengenai struktur CSS Grid dan media query untuk merapikan layout responsif pada perangkat mobile. dan juga untuk fitur ektstra saya pun menanyakan ke AI apa yang harus saya lakukan dan harus saya tulis ketika saya mau fitur dark theme pada website saya. Untuk keperluan git juga saya menanyakan kepada AI terlebih ketika berkomunikasi melalui terminal. 

Beberapa prompt yang saya gunakan: 

1. Tolong ubah tutorial berikut dengan lengkap dan ubah agar menjadi poin poin yang berurut agar saya dapat dengan mudah melihat step by step yang diberikan oleh link tutorial berikut.

2. Tolong ajarkan saya dalam menambahkan tugas yang di berikan yaitu memberikan beberapa section, agar sesuai dengan ketentuan yang di berikan oleh soal, guide saya dalam mengerjakan, pada awal jangan berikan saya code jadinya terlebih dahulu, ajarkan saya alur pengerjaan, ketika saya sudah stuck baru dengan perlahan berikan saya code yang harus ditulis pada css dan html saya.


TUGAS 02
PERTANYAAN REFLEKTIF


1. Alur Request-Response MVT:

urls.py Proyek: Menerima permintaan dari browser dan mengarahkannya ke urls.py aplikasi.
urls.py Aplikasi: Mencocokkan pola URL spesifik dan memanggil fungsi view yang sesuai.
View (views.py): Bertindak sebagai pengendali logika, meminta data ke Model, lalu membungkusnya ke dalam context.
Model (models.py): Berinteraksi dengan basis data menggunakan ORM untuk mengambil data portofolio.
Template (.html): Merender data yang diterima dari view menggunakan DTL (Django Template Language) untuk ditampilkan ke browser.

2. Alasan Model vs. Hard-coded di Template:

Pemisahan Tugas: Memisahkan lapisan tampilan (template) dengan isi data (model).
Pemeliharaan Mudah: Penambahan atau perubahan data portofolio bisa dilakukan lewat admin Django atau basis data tanpa harus mengubah kode HTML berulang kali.
Dinamis & Skalabel: Data dapat dirender secara otomatis menggunakan looping, sehingga aplikasi lebih fleksibel saat data bertambah.

3. Perbedaan makemigrations dan migrate:

makemigrations: Berfungsi mendeteksi perubahan pada models.py dan membuat berkas cetak biru (blueprint) migrasi. Perintah ini belum mengubah basis data fisik.
migrate: Berfungsi menerapkan cetak biru migrasi tersebut agar tabel/kolom benar-benar terbentuk di dalam basis data.
Contoh Kasus: Saat membuat model baru seperti Project, jalankan makemigrations untuk membuat instruksinya, lalu jalankan migrate untuk mengeksekusi pembuatan tabel di basis data.


AI Disclosure

Untuk pengerjaan Individual Assignment 2 ini, strategi utama saya adalah memanfaatkan AI (Gemini) untuk membantu memahami alur implementasi arsitektur Model View Template (MVT) pada Django secara bertahap agar proses pengerjaan lebih terarah. AI membantu saya memecah instruksi tugas yang ada di halaman tugas menjadi poin-poin langkah demi langkah yang sistematis.

Beberapa contoh prompt yang saya gunakan:

1. Tolong jelaskan alur request response MVT di Django secara sederhana dan berurutan dari urls proyek, urls aplikasi, view, model, hingga template untuk menjawab pertanyaan reflektif tugas.

2. Tolong pandu saya langkah demi langkah dalam membuat model Project baru dengan minimal tiga field, membuat migrasinya, lalu menampilkannya menggunakan perulangan Django Template Language di halaman HTML khusus project tanpa memberikan kode instan sekaligus.

