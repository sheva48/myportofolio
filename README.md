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


TUGAS 03
PERTANYAAN REFLEKTIF

1. Kenapa ModelForm, bukan HTML form manual? Kenapa perlu {% csrf_token %}?

ModelForm otomatis generate field form dari field yang udah ada di model, jadi gak perlu nulis ulang tiap <input> manual. Validasinya juga otomatis ngikutin constraint model (max_length, choices, format URL, dll), dan udah ada method .save() buat langsung nyimpen ke DB. Kalau manual, semua validasi & proses simpan itu tanggung jawab kita sendiri lebih ribet dan gampang meleset kalau model berubah.

{% csrf_token %} wajib buat nyegah Cross-Site Request Forgery biar situs lain gak bisa diam-diam ngirim request POST (misal hapus/tambah data) atas nama user yang lagi login. Django kasih token unik per-session, dan nolak POST yang gak bawa token itu (403).

2. Kenapa JSON lebih disukai daripada XML?

JSON lebih ringkas gak ada tag pembuka-penutup berulang kayak XML, jadi payload-nya lebih kecil dan cepat. Strukturnya juga langsung mirip objek JavaScript, jadi browser bisa langsung JSON.parse() tanpa library tambahan. Sintaksnya lebih gampang dibaca dan hampir semua bahasa modern udah dukung JSON native. XML lebih verbose dan awalnya didesain buat dokumen kompleks dengan schema/namespace, yang kebanyakan gak dibutuhin buat API sederhana.

3. Alur view balikin data sebagai JSON, dan kenapa perlu serialization?

View query data dari DB lewat ORM (Education.objects.all()), hasilnya QuerySet berisi objek Python (model instance), objek ini gak bisa langsung dikirim lewat HTTP karena HTTP cuma ngirim teks, makanya dipakai serializers.serialize("json", queryset) buat ubah objek jadi string JSON, dibungkus HttpResponse dan dikirim ke client.

Serialization perlu karena ada gap antara representasi data di memori Python (objek spesifik Django) dengan format yang bisa dipahami universal lewat jaringan (teks). Tanpa itu, sistem lain di luar Python/Django (browser, app lain) gak bakal ngerti objeknya.

AI Disclosure

Untuk pengerjaan Individual Assignment 3 ini, saya memanfaatkan AI (Claude) terutama buat bantu nerapin alur Form dan Data Delivery di Django — mulai dari bikin ModelForm, function-based view buat create/update/delete, sampai serialisasi data ke JSON dan nampilinnya lagi di template. Saya juga minta AI bantu jelasin konsep di balik tiap bagian (kenapa perlu CSRF token, kenapa JSON dipakai dibanding XML, alur serialization) biar gak cuma copy-paste tapi ngerti alasannya, dan minta dipecah jadi tahapan kecil biar progress gampang di-commit bertahap. Selain itu AI juga saya pakai buat debugging waktu migrasi database sempat gagal di server production (PWS) gara-gara perubahan tipe primary key yang gak kompatibel sama PostgreSQL.

Beberapa contoh prompt yang saya gunakan:

Tolong jelasin dulu isi requirement Tugas 3 ini apa aja dan aku udah sampai mana, jangan langsung dikerjain dulu.

Bikinin fitur CRUD lengkap (create, update, delete) plus endpoint JSON buat section Education, tapi progressnya dipecah jadi beberapa tahap dan di-commit satu-satu, bukan sekaligus.

Kenapa migrasi project_url gagal di server production padahal di lokal jalan lancar? Tolong jelasin penyebabnya sebelum dibenerin.


TUGAS 04

Untuk pengerjaan Individual Assignment 4 ini, saya memanfaatkan AI (Claude) buat bantu nerapin authentication, session/cookies, dan authorization berbasis role di Django mulai dari register/login/logout, cookie last_login, sampai bikin role Editor pakai Django Group dan ngatur empat tingkat akses (pengunjung anonim, user biasa, Editor, dan owner). Sebelum mulai ngoding, saya minta AI jelasin dulu isi requirement tugasnya dan bandingin sama kode yang udah ada, jadi ketahuan mana yang belum dikerjain ternyata fitur update untuk Project belum pernah ada sama sekali. Di akhir, AI bantu saya nemuin celah di endpoint JSON publik yang ternyata ngebocorin username semua orang yang nge-star sebuah project, lalu saya benerin dengan membatasi field mana aja yang boleh keluar ke publik.

Beberapa contoh prompt yang saya gunakan:

Jelasin dulu isi tugas ini apa aja dan aku udah sampai mana.


Endpoint JSON-nya aman gak? Cek apakah ada data user yang kebocoran ke publik.

TUGAS 05

1. Apa itu debouncing dan kenapa penting di pencarian AJAX?

Debouncing adalah teknik untuk menunda eksekusi sebuah fungsi sampai ada jeda waktu tertentu tanpa event baru. Selama user masih ngetik, timer sebelumnya dibatalin terus dimulai ulang, jadi fungsinya akan baru benar-benar jalan setelah user berhenti ngetik sejenak.

Hal berikut penting di pencarian AJAX karena tanpa debouncing, setiap karakter yang diketik bakal ngirim satu request. Ngetik "Django" saja berarti enam request beruntun ke server, padahal lima di antaranya langsung basi. Selain boros buat server, ini juga bikin masalah urutan: response dari ketikan lama bisa datang belakangan dan nimpa hasil pencarian yang lebih baru. Di proyek ini saya pakai jeda 300ms, cukup singkat biar tetap terasa responsif tapi cukup panjang buat nahan request berulang. Saya juga nambahin AbortController buat ngebatalin request lama yang belum selesai, jadi hasil yang usang gak mungkin nimpa yang terbaru.

2. Fungsi await di fetch() dan apa jadinya kalau gak dipakai?

fetch() itu gak langsung balikin datanya, tapi balikin Promise semacam janji bahwa datanya bakal ada nanti. await fungsinya nahan jalannya fungsi async sampai Promise itu selesai, baru ngasih nilai aslinya, yaitu object Response.

Kalau await tidak dipakai, variabelnya bakal keisi object Promise, bukan Response. Jadi response.ok nilainya undefined dan response.json() bakal error karena Promise gak punya method itu. Selain itu kode di bawahnya langsung jalan padahal datanya belum sampai, jadi hasilnya kosong. response.json() sendiri juga balikin Promise, makanya dia juga perlu await.

Sebenarnya await ini cuma cara penulisan yang lebih rapi dari .then(). Dua-duanya nunggu Promise selesai, tapi await bikin alurnya kebaca dari atas ke bawah kayak kode biasa, dan error-nya bisa ditangkap pakai try...catch biasa.

3. Apa itu XSS dan kenapa data lewat AJAX lebih rentan daripada lewat template Django?

Cross-Site Scripting adalah serangan ketika penyerang berhasil menyisipkan kode JavaScript miliknya ke halaman web, lalu kode itu dijalankan di browser pengguna lain. Jenis yang dipakai di tutorial adalah stored XSS, yaitu kode jahatnya tersimpan di database (misalnya sebagai nama institusi) dan ikut dieksekusi tiap kali data itu ditampilkan. Dampaknya bukan sekadar munculnya alert: cookie csrftoken bisa dibaca JavaScript, jadi kode sisipan bisa ngirim permintaan POST atas nama korban, misalnya ngehapus data kalau korbannya pemilik portofolio.

Data lewat template Django relatif aman karena Django otomatis melakukan auto-escaping pada setiap variabel. Karakter < dan > diubah jadi &lt; dan &gt;, sehingga browser nampmenampilkan tag HTML sebagai teks biasa, bukan sebagai kode. Perlindungan otomatis itu hilang begitu data dirakit sendiri lewat JavaScript, karena nilai dari JSON disisipin ke template literal lalu dipasang pakai innerHTML — dan innerHTML memang mengartikan isinya sebagai HTML sungguhan. Gak ada lagi Django yang nyaring di tengah jalan. Karena itu di proyek ini saya nulis fungsi escapeHtml sendiri dan ngebungkus setiap nilai teks yang masuk ke HTML, plus nambahin strip_tags pada method clean_<field> di ModelForm sebagai lapisan kedua di sisi server.

AI Disclosure

Untuk Individual Assignment 5 ini saya memakai AI (Claude) sebagai pasangan kerja dalam menulis implementasi, sementara arah dan keputusan teknisnya saya yang pegang. Pertama, saya menolak memakai UUID pada id Project seperti di tutorial, dan memilih tetap integer. Alasannya pada tugas sebelumnya migrasi UUID sempat menggagalkan deployment di PWS karena PostgreSQL tidak bisa mengonversi kolom integer yang sudah berisi data.

Kedua, tutorial meminta endpoint JSON menampilkan starred_by_names, yaitu daftar username pemberi star. Saya menolak menerapkannya apa adanya karena endpoint itu publik dan pada Tugas 4 saya justru menutup kebocoran yang sama. Saya memilih jalan tengah: field-nya tetap ada, tapi isinya hanya keluar untuk pemilik portofolio.

Peran AI terbesar ada pada penulisan kode implementasi: view AJAX, skrip fetch beserta penanganan loading/kosong/error, debouncing, modal, serta lapisan perlindungan XSS. Saya juga meminta penjelasan konsep di balik tiap bagian, misalnya kenapa serializers.serialize tidak bisa dipakai lagi ketika data harus membawa status star pengguna yang sedang login, supaya saya paham alasannya dan bukan sekadar menyalin. Hasilnya saya periksa lewat tampilan di browser, dan beberapa kali saya minta perbaiki, misalnya posisi tombol Login dan Register yang tidak sejajar, serta kartu yang tampil ganda pada carousel halaman utama.

Beberapa contoh prompt yang saya gunakan:

Endpoint JSON-nya aman tidak? Cek apakah ada data pengguna yang bocor ke publik.

Uji perlindungan XSS-nya dengan payload yang ada di tutorial, lalu tunjukkan data yang akhirnya tersimpan di database.

