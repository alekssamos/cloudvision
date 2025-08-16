### Pilvinäkö

Tässä lisäosassa on seuraavat ominaisuudet:
* Valokuvien kuvailu (esim. hymyilevä 23-vuotias tyttö, jolla on vaaleat hiukset)
* Tekstintunnistus
* Tekstin kääntäminen toiselle kielelle
* QR- ja viivakoodien lukeminen
* Matemaattisten kaavojen tunnistus Mathpixin avulla

### Lisäosan asetukset
Avaa NVDA-valikko, siirry Asetukset-alivalikkoon ja valitse "Pilvinäkö..." -vaihtoehto.

### Pikanäppäimet
* NVDA+Ctrl+I: Tunnista navigointiobjekti tai valittu tiedosto Resurssienhallinnassa. Kahdesti painettaessa tulos näytetään erillisessä ikkunassa.
* NVDA+Alt+F: Tunnista koko ruutu.
* NVDA+Alt+C: Tunnista leikepöydällä oleva kuva.
* NVDA+Alt+A: Esitä kysymys Be My AI:lle (sinun täytyy kirjautua olemassa olevalle tilillesi tai rekisteröityä lisäosan asetuksissa).
* Ei määritettyä näppäinkomentoa: Analysoi objekti Mathpixillä (matemaattisia kaavoja varten). Määritä näppäinkomento siirtymällä NVDA-valikkoon, avaamalla Asetukset-alivalikko, valitsemalla Näppäinkomennot-vaihtoehto ja sitten Pilvinäkö-kategoria.
* Ei määritettyä näppäinkomentoa: Kopioi viimeisin tulos leikepöydälle. Määritä näppäinkomento siirtymällä NVDA-valikkoon, avaamalla Asetukset-alivalikko, valitsemalla Näppäinkomennot-vaihtoehto ja sitten Pilvinäkö-kategoria.

Tunnistuta navigointiobjekti siirtämällä se haluamaasi paikkaan ja painamalla asianmukaista pikanäppäintä, jonka jälkeen lisäosa tunnistaa sen.
Tiedoston tunnistus tapahtuu valitsemalla se Resurssienhallinnassa ja painamalla tunnistuspikanäppäintä.
Vain jpg-, png- ja gif-formaatteja tuetaan.
PDF-tukea ei ole lisätty, koska sen tunnistus voi kestää 40 minuuttia tai kauemminkin.

Valittujen tiedostojen idea ja koodi on otettu Nao (NVDA Advanced OCR) -lisäosasta.

Kirjautumista Googlen, Applen tai muiden palveluiden kautta ei tueta. Jos virheitä ilmenee, luo uusi tili uutta, toimivaa sähköpostiosoitetta käyttäen.

### Mathpix-integraatio

Mathpixin käyttäminen matemaattisten kaavojen ja yhtälöiden tunnistamiseen:

1. Hanki API-avain [mathpix.com](https://mathpix.com)-sivustolta
2. Syötä API-avaimesi Pilvinäön asetusikkunaan
3. Ota käyttöön "Käytä Mathpixiä matemaattisten kaavojen tunnistamiseen" -asetus

Voit käyttää Mathpixiä kahdella tavalla:
* Kun asetus on käytössä, Mathpixiä käytetään muiden tunnistuspalveluiden rinnalla tavallisen tunnistuksen aikana (NVDA+Ctrl+I)
* Voit määrittää pikanäppäimen "Analysoi objekti Mathpixillä" -komennolle NVDA:n näppäinkomentovalintaikkunassa käyttääksesi Mathpixiä suoraan
