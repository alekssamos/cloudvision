### CloudVision:

Eklenti, fotoğrafların bir açıklamasını sağlar; örneğin, sarı saçlı gülümseyen 23 yaşındaki bir kız.
Metin tanıma, başka bir dile metin çevirisi, QR kodlarını okuma ve Mathpix ile matematiksel formülleri tanıma.

### Eklenti ayarları:
NVDA menüsü, Tercihler, CloudVision Ayarları'nı açın.  

### Klavye kısayolları:
* NVDA + CTRL + I - Nesne veya seçilen dosyayı Explorer'da tanır. Hızlıca iki kez basarsanız, sonuç sanal görüntüleme penceresinde görünecektir.
* NVDA+ALT+A - Be My AI'ye bir soru sorun (hesabınızda oturum açmanız veya CloudVision ayarları aracılığıyla kaydolmanız gerekir)
* hareket atanmadı - Mathpix ile nesneyi analiz edin (matematiksel formüller için). Atamak için bkz. NVDA menüsü, Tercihler, girdi hareketleri, CloudVision kategorisi.
* hareket atanmadı - son sonucu panoya kopyalayın. Atamak için bkz. NVDA menüsü, Tercihler, girdi hareketleri, CloudVision kategorisi.

Nesne için: dilediğiniz bir nesneyi seçin ve tanımlanmış harekete basın. Eğer hızlıca iki defa basarsanız, sonuç sanal bir pencerede görüntülenecektir.  
Bir dosya için: Desteklenen bir dosyanın üzerine gelin, açmadan seçili hale getirin ve tanımlanmış harekete basın.  
Yalnızca JPG, PNG, GIF desteklenir.  
Tanıma süresi 40 dakika veya daha uzun olabileceğinden PDF eklemedim.  

Seçilen dosyalar için fikir ve kod "Nao (NVDA Advanced OCR)" eklentisinden alınmıştır.  

Google, Apple ve diğer hizmetlerle oturum açma desteklenmemektedir.  
Bir hata oluşursa lütfen farklı bir e-posta adresiyle yeni bir hesap oluşturun.

### Mathpix Entegrasyonu

Matematiksel formülleri ve denklemleri tanımak için Mathpix kullanmak için:

1. [mathpix.com](https://mathpix.com) adresinden bir API anahtarı alın
2. API anahtarınızı CloudVision ayarları iletişim kutusuna girin
3. "Matematik formüllerini tanıma için Mathpix kullan" seçeneğini etkinleştirin

Mathpix'i iki şekilde kullanabilirsiniz:
* Ayarlarda etkinleştirildiğinde, Mathpix standart tanıma sırasında (NVDA+CTRL+I) diğer tanıma hizmetleriyle birlikte kullanılacaktır
* Mathpix'i doğrudan kullanmak için NVDA'nın girdi hareketleri iletişim kutusunda "Mathpix ile nesneyi analiz et" komutuna bir klavye kısayolu atayabilirsiniz
