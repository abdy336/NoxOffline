import os
import json
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Color, Ellipse, StencilPush, StencilUse, StencilUnUse, StencilPop, RoundedRectangle, Rectangle
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner

# --- AYARLAR ---
Window.clearcolor = (0, 0, 0, 1)
DATA_FILE = "filmler.json"

# --- YARDIMCI SINIFLAR (DEĞİŞTİRİLMEDİ) ---
class ModernFilterButton(Button):
    def __init__(self, **kwargs):
        self.row_type = kwargs.pop('row_type', 'top')
        super(ModernFilterButton, self).__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (0.9, 0.9, 0.9, 1)
        self.font_size = kwargs.get('font_size', '11sp')
        self.bold = True
        self.bg_color = (0.12, 0.12, 0.12, 1)
        with self.canvas.before:
            self.color_instr = Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_active(self, active=True):
        if active:
            if self.row_type == 'bottom':
                self.color_instr.rgba = (0.5, 0, 0.8, 1)
            else:
                self.color_instr.rgba = (0.1, 0.4, 0.8, 1)
        else:
            self.color_instr.rgba = (0.12, 0.12, 0.12, 1)

class ModernSearchInput(BoxLayout):
    def __init__(self, **kwargs):
        hint = kwargs.pop('hint_text', '')
        multi = kwargs.pop('multiline', False)
        varsayilan_text = kwargs.pop('text', '')
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', '50dp' if not multi else '120dp')
        super(ModernSearchInput, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        self.bind(pos=self._update, size=self._update)
        self.input = TextInput(
            text=varsayilan_text,
            hint_text=hint, multiline=multi, background_normal="", background_active="",
            background_color=(0, 0, 0, 0), foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1), hint_text_color=(0.5, 0.5, 0.5, 1),
            font_size='16sp', padding=[15, 12, 10, 10]
        )
        self.add_widget(self.input)
    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    @property
    def text(self): return self.input.text
    @text.setter
    def text(self, val): self.input.text = val

class RoundImage(Image):
    def __init__(self, **kwargs):
        super(RoundImage, self).__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas)
    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            StencilPush(); Ellipse(pos=self.pos, size=self.size); StencilUse()
        self.canvas.after.clear()
        with self.canvas.after:
            StencilUnUse(); Ellipse(pos=self.pos, size=self.size); StencilPop()

class IcerikKismi(ButtonBehavior, BoxLayout):
    pass

class BadgeLabel(Label):
    def __init__(self, **kwargs):
        super(BadgeLabel, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 0.75) 
            self.bg = RoundedRectangle(radius=[6])
        self.bind(pos=self._update, size=self._update)
    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

class RoundedPoster(FloatLayout):
    def __init__(self, kaynak, bilgi_text, **kwargs):
        super(RoundedPoster, self).__init__(**kwargs)
        with self.canvas.before:
            StencilPush()
            self.rect = RoundedRectangle(radius=[15])
            StencilUse()
        self.img = Image(source=kaynak, allow_stretch=True, keep_ratio=False, pos_hint={'x':0, 'y':0}, size_hint=(1,1))
        self.add_widget(self.img)
        with self.canvas.after:
            StencilUnUse()
            self.rect2 = RoundedRectangle(radius=[15])
            StencilPop()
        self.bind(pos=self._update, size=self._update)
        self.top_badge = BadgeLabel(text="18+", font_size='10sp', bold=True, size_hint=(None, None), size=('32dp', '20dp'), pos_hint={'x': 0.05, 'top': 0.95})
        self.add_widget(self.top_badge)
        k_bilgi = bilgi_text[:12] + ".." if len(bilgi_text) > 12 else bilgi_text
        if not k_bilgi: k_bilgi = "HD"
        self.bot_badge = BadgeLabel(text=k_bilgi, font_size='10sp', bold=True, size_hint=(None, None), size=('65dp', '20dp'), pos_hint={'x': 0.05, 'y': 0.05})
        self.add_widget(self.bot_badge)
    def _update(self, *args):
        self.rect.pos = self.pos; self.rect.size = self.size
        self.rect2.pos = self.pos; self.rect2.size = self.size

class OfflineGridKarti(BoxLayout):
    def __init__(self, veri, ana_kategori, **kwargs):
        super(OfflineGridKarti, self).__init__(**kwargs)
        self.veri = veri
        self.ana_kategori = ana_kategori
        self.orientation = 'vertical'; self.size_hint_y = None; self.spacing = 8
        icerik = IcerikKismi(orientation='vertical')
        icerik.bind(on_release=self.ac)
        resim_yolu = veri['foto'] if os.path.exists(veri['foto']) else "offline.jpeg"
        self.poster = RoundedPoster(kaynak=resim_yolu, bilgi_text=veri['bilgi'])
        
        if self.ana_kategori == "Aýdym-saz":
            self.poster.top_badge.opacity = 0
            self.poster.bot_badge.opacity = 0
            
        icerik.add_widget(self.poster); self.add_widget(icerik)
        alt = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp')
        self.isim = Label(text=veri['ad'], bold=True, font_size='14sp', halign='left', valign='top', color=(0.9,0.9,0.9,1), shorten=True)
        self.isim.bind(size=self.isim.setter('text_size'))
        sil_btn = Button(text="⋮", font_size='22sp', size_hint_x=None, width='30dp', background_color=(0,0,0,0), color=(0.7,0.7,0.7,1))
        sil_btn.bind(on_release=self.islem_menusu) 
        alt.add_widget(self.isim); alt.add_widget(sil_btn); self.add_widget(alt)
        self.bind(width=self._update_height)

    def _update_height(self, *args):
        if self.ana_kategori == "Aýdym-saz":
            self.height = self.width * 0.56 + 50
        else:
            self.height = self.width * 1.45 + 40

    def ac(self, *args):
        if self.veri['link'].startswith("http"): webbrowser.open(self.veri['link'])

    def islem_menusu(self, *args):
        icerik = BoxLayout(orientation='vertical', padding=10, spacing=10)
        duzelt_btn = Button(text="Düzelt", size_hint_y=None, height='50dp', background_color=(0.1, 0.5, 0.8, 1))
        sil_btn = Button(text="Pozmak", size_hint_y=None, height='50dp', background_color=(0.8, 0.2, 0.2, 1))
        icerik.add_widget(duzelt_btn); icerik.add_widget(sil_btn)
        self.menu_popup = Popup(title="Saýlaň", content=icerik, size_hint=(0.7, 0.3))
        duzelt_btn.bind(on_release=self.duzenle_popup)
        sil_btn.bind(on_release=self.silme_onayi)
        self.menu_popup.open()

    def duzenle_popup(self, *args):
        self.menu_popup.dismiss()
        l = BoxLayout(orientation='vertical', padding=15, spacing=10)
        self.edit_ad = ModernSearchInput(hint_text='Ady', text=self.veri['ad'])
        self.edit_bilgi = ModernSearchInput(hint_text='Maglumat', text=self.veri['bilgi'], multiline=True)
        self.edit_foto = ModernSearchInput(hint_text='Foto', text=self.veri['foto'])
        self.edit_link = ModernSearchInput(hint_text='Link', text=self.veri['link'])
        kaydet = Button(text="Ýatda Sakla", size_hint_y=None, height='50dp', background_color=(0.1, 0.6, 0.1, 1))
        kaydet.bind(on_release=self.duzenle_kaydet)
        l.add_widget(self.edit_ad); l.add_widget(self.edit_bilgi); l.add_widget(self.edit_foto); l.add_widget(self.edit_link); l.add_widget(kaydet)
        self.edit_p = Popup(title="Düzeltmek", content=l, size_hint=(0.9, 0.8)); self.edit_p.open()

    def duzenle_kaydet(self, *args):
        yeni_veri = self.veri.copy() 
        yeni_veri.update({'ad': self.edit_ad.text, 'bilgi': self.edit_bilgi.text, 'foto': self.edit_foto.text, 'link': self.edit_link.text})
        App.get_running_app().veri_guncelle(self.veri, yeni_veri)
        self.edit_p.dismiss(); App.get_running_app().sm.get_screen('offline_page').yukle()

    def silme_onayi(self, *args):
        self.menu_popup.dismiss()
        p_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        p_layout.add_widget(Label(text=f"{self.veri['ad']}\npozulsinmy?", halign='center', font_size='18sp'))
        btns = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        evet = Button(text="Hawa", background_color=(0.8, 0.2, 0.2, 1), bold=True)
        hayir = Button(text="Ýok", background_color=(0.3, 0.3, 0.3, 1))
        btns.add_widget(evet); btns.add_widget(hayir); p_layout.add_widget(btns)
        self.popup = Popup(title="Pozmak", content=p_layout, size_hint=(0.8, 0.4))
        evet.bind(on_release=self.sil); hayir.bind(on_release=self.popup.dismiss); self.popup.open()

    def sil(self, *args):
        App.get_running_app().veri_sil(self.veri)
        self.popup.dismiss(); App.get_running_app().sm.get_screen('offline_page').yukle()

# --- EKRANLAR (SADECE OFFLINE KALDI) ---
class OfflineScreen(Screen):
    def on_enter(self): self.yukle()
    def __init__(self, **kwargs):
        super(OfflineScreen, self).__init__(**kwargs)
        self.secili_ust = "Filmler"
        self.secili_alt = None 
        self.l = BoxLayout(orientation='vertical', padding=15, spacing=15)
        ust = BoxLayout(size_hint_y=None, height='50dp')
        ust.add_widget(Label(text="Offline Bölümi", bold=True, font_size='22sp', halign='left'))
        btn = Button(text="+ Täze", size_hint_x=None, width='80dp', background_color=(0.1, 0.4, 0.1, 1))
        btn.bind(on_release=self.ekle_sayfasina_gec)
        ust.add_widget(btn); self.l.add_widget(ust)
        
        self.ust_btns = {}
        filtre_box = BoxLayout(orientation='horizontal', size_hint_y=None, height='35dp', spacing=8)
        for isim in ["Filmler", "Seriallar", "Multfilmler", "Aýdym-saz"]:
            b = ModernFilterButton(text=isim, row_type='top')
            b.bind(on_release=self.filtre_tikla)
            filtre_box.add_widget(b)
            self.ust_btns[isim] = b
        self.ust_btns["Filmler"].set_active(True)
        self.l.add_widget(filtre_box)

        self.alt_filtre_box = BoxLayout(orientation='horizontal', size_hint_x=None, spacing=6, padding=[0, 2])
        self.alt_filtre_box.bind(minimum_width=self.alt_filtre_box.setter('width'))
        self.alt_scroll = ScrollView(size_hint_y=None, height='28dp', do_scroll_x=True, do_scroll_y=False)
        self.alt_scroll.add_widget(self.alt_filtre_box)
        self.l.add_widget(self.alt_scroll)

        self.alt_btns = {}
        self.alt_kategorileri_olustur(["Boýewik", "Komediýa", "Gorky", "Taryh", "Maşgala", "Fantastika", "Drama"])

        self.grid = GridLayout(cols=2, spacing=15, size_hint_y=None); self.grid.bind(minimum_height=self.grid.setter('height'))
        sc = ScrollView(); sc.add_widget(self.grid); self.l.add_widget(sc); self.add_widget(self.l)

    def alt_kategorileri_olustur(self, turler):
        self.alt_filtre_box.clear_widgets()
        self.alt_btns = {}
        for isim in turler:
            b = ModernFilterButton(text=isim, font_size='8sp', size_hint_x=None, width='80dp', row_type='bottom')
            b.bind(on_release=self.filtre_tikla)
            self.alt_filtre_box.add_widget(b)
            self.alt_btns[isim] = b

    def filtre_tikla(self, instance):
        isim = instance.text
        if instance.row_type == 'top':
            for b in self.ust_btns.values(): b.set_active(False)
            instance.set_active(True)
            self.secili_ust = isim
            self.secili_alt = None 
            if isim == "Aýdym-saz":
                self.alt_kategorileri_olustur(["BLACKPINK", "Hemra Rejepow", "Azat Dönmezow", "Başga"])
            else:
                self.alt_kategorileri_olustur(["Boýewik", "Komediýa", "Gorky", "Taryh", "Maşgala", "Fantastika", "Drama"])
        else:
            if self.secili_alt == isim:
                instance.set_active(False)
                self.secili_alt = None
            else:
                for b in self.alt_btns.values(): b.set_active(False)
                instance.set_active(True)
                self.secili_alt = isim
        self.yukle()

    def yukle(self):
        self.grid.clear_widgets()
        self.grid.cols = 1 if self.secili_ust == "Aýdym-saz" else 2
        for f in App.get_running_app().verileri_yukle():
            if f.get('ana_kat', 'Filmler') == self.secili_ust:
                if self.secili_alt is None or f.get('kat') == self.secili_alt:
                    self.grid.add_widget(OfflineGridKarti(f, self.secili_ust))

    def ekle_sayfasina_gec(self, *args):
        App.get_running_app().sm.get_screen('film_ekle').kat_secici.text = self.secili_alt if self.secili_alt else self.secili_ust
        App.get_running_app().sm.current = 'film_ekle'

class FilmEkleScreen(Screen):
    def __init__(self, **kwargs):
        super(FilmEkleScreen, self).__init__(**kwargs)
        l = BoxLayout(orientation='vertical', padding=20, spacing=15)
        tum = ('Boýewik', 'Komediýa', 'Gorky', 'Taryh', 'Maşgala', 'Fantastika', 'Drama', 'Hemra Rejepow', 'Azat Dönmezow', 'BLACKPINK', 'Başga')
        self.kat_secici = Spinner(text='Boýewik', values=tum, size_hint_y=None, height='45dp')
        self.ad = ModernSearchInput(hint_text='Ady'); self.bilgi = ModernSearchInput(hint_text='Kyssa', multiline=True)
        self.foto = ModernSearchInput(hint_text='Foto'); self.link = ModernSearchInput(hint_text='Link')
        btn = Button(text="Ýatda Sakla", size_hint_y=None, height='60dp', background_color=(0.1, 0.4, 0.8, 1), bold=True)
        btn.bind(on_release=self.kaydet)
        l.add_widget(self.kat_secici); l.add_widget(self.ad); l.add_widget(self.bilgi); l.add_widget(self.foto); l.add_widget(self.link); l.add_widget(btn); self.add_widget(l)
    def kaydet(self, *args):
        if self.ad.text:
            ana = App.get_running_app().sm.get_screen('offline_page').secili_ust
            App.get_running_app().veri_kaydet({'ad': self.ad.text, 'bilgi': self.bilgi.text, 'foto': self.foto.text, 'link': self.link.text, 'kat': self.kat_secici.text, 'ana_kat': ana})
            App.get_running_app().sm.current = 'offline_page'

# --- ANA UYGULAMA (SADECE OFFLINE MODU) ---
class NoxPlayer(App):
    def build(self):
        self.sm = ScreenManager(transition=FadeTransition())
        # Sadece gerekli ekranlar
        self.sm.add_widget(OfflineScreen(name='offline_page'))
        self.sm.add_widget(FilmEkleScreen(name='film_ekle'))
        
        # Başlangıç ekranını Offline yapıyoruz
        self.sm.current = 'offline_page'
        return self.sm

    def verileri_yukle(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
            except: return []
        return []
    def veri_kaydet(self, yeni):
        m = self.verileri_yukle(); m.append(yeni)
        with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(m, f, ensure_ascii=False, indent=4)
    def veri_guncelle(self, eski, yeni):
        m = self.verileri_yukle()
        for i, item in enumerate(m):
            if item.get('ad') == eski.get('ad'):
                m[i] = yeni
                break
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=4)
    def veri_sil(self, sil_veri):
        m = self.verileri_yukle()
        yeni_m = [f for f in m if f.get('ad') != sil_veri.get('ad')]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(yeni_m, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    NoxPlayer().run()
  
