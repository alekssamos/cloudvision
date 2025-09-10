### Pilvinäkö

Tämän lisäosan avulla on mahdollista saada kuvan kuvaus tekoälyä käyttäen.

Se hyödyntää Google Chromen tekstintunnistusta, PiccyBotia ja Mathpix-palvelua matemaattisten kaavojen ja yhtälöiden tunnistamiseen.

Aiemmin käytössä olivat myös Microsoft ja Be My Eyes, mutta Microsoft esti pääsyn palveluunsa ja Be My Eyes alkoi suojautua epäviralliselta rajapinnan käytöltä.

Lisäosan asetukset löytyvät kohdasta NVDA-valikko > Mukautukset > Pilvinäön asetukset.

Pikanäppäimet:

* NVDA+Ctrl+I: Kuvaile navigointiobjekti tai valittuna oleva JPG/PNG-kuva Resurssienhallinnassa. Kahdesti painettaessa tulos avautuu virtuaaliseen ikkunaan, jossa voit lukea sitä nuolilla, valita, kopioida jne.
* NVDA+Alt+F: Tunnista koko ruutu.
* NVDA+Alt+W: Tunnista aktiivinen ikkuna.
* NVDA+Alt+C: Tunnista leikepöydällä oleva kuva.
* NVDA+Alt+A: Esitä botille kysymys viimeksi tunnistetusta kuvasta.
* Analysoi objekti Mathpixillä (matemaattisia kaavoja varten): Näppäinkomentoa ei ole määritetty. Voit määrittää sen Näppäinkomennot-valintaikkunassa.
* Kopioi viimeisin tunnistuksen tulos leikepöydälle: Pikanäppäintä ei ole määritetty. Voit määrittää sen Näppäinkomennot-valintaikkunassa.
* NVDA+Alt+P: Vaihtaa kehotetta (lyhyt, yksityiskohtainen, oma).

### Mathpix-integraatio

Mathpixin käyttäminen matemaattisten kaavojen ja yhtälöiden tunnistamiseen:

1. Hanki API-avain [mathpix.com](https://mathpix.com)-sivustolta
2. Syötä saamasi avain Pilvinäön asetusikkunaan
3. Ota käyttöön asetus "Käytä Mathpixiä matemaattisten kaavojen tunnistamiseen"

Voit käyttää Mathpixiä kahdella tavalla:
* Kun asetus on käytössä, Mathpixiä käytetään muiden tunnistuspalveluiden rinnalla tavallisen tunnistuksen aikana (NVDA+Ctrl+I)
* Voit käyttää Mathpixiä suoraan määrittämällä pikanäppäimen komennolle "Analysoi objekti Mathpix-palvelulla" NVDA:n Näppäinkomennot-valintaikkunassa

