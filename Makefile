DEST=/usr
L10N=fr en_US
PKGNAME=hubic-gtk
ICON_THEME=theme1
#PKGVER=dev

all: build install

build:
	cp $(PKGNAME).py $(PKGNAME)
	sed -i "s|HUBIC_L10N_PATH = './po'|HUBIC_L10N_PATH = '$(DEST)/share/locale'|" $(PKGNAME)
	sed -i "s|HUBIC_STATUS_VERSION = 'dev'|HUBIC_STATUS_VERSION = '$(PKGVER)'|" $(PKGNAME)

install: install-bin install-lang

install-bin:
	install -d -m755	$(DEST)/bin
	install -d -m755	$(DEST)/share/applications
	install -d -m755	$(DEST)/share/licenses/$(PKGNAME)
	install -d -m755	$(DEST)/share/icons/gnome/scalable/apps
	install -d -m755	$(DEST)/share/icons/gnome/scalable/status
	install -d -m755	$(DEST)/share/icons/hicolor/scalable/apps
	install -d -m755	$(DEST)/share/icons/hicolor/scalable/status

	install -D -m755 $(PKGNAME)                             $(DEST)/bin/$(PKGNAME)
	install -D -m644 $(PKGNAME).desktop                     $(DEST)/share/applications
	install -D -m644 LICENSE                                $(DEST)/share/licenses/$(PKGNAME)/LICENSE
	install -D -m644 data/${ICON_THEME}/hubic-gtk.svg       $(DEST)/share/icons/gnome/scalable/apps/hubic-gtk.svg
	install -D -m644 data/${ICON_THEME}/hubic-gtk-alert.svg $(DEST)/share/icons/gnome/scalable/status/hubic-gtk-alert.svg
	install -D -m644 data/${ICON_THEME}/hubic-gtk-busy.svg  $(DEST)/share/icons/gnome/scalable/status/hubic-gtk-busy.svg
	install -D -m644 data/${ICON_THEME}/hubic-gtk.svg       $(DEST)/share/icons/hicolor/scalable/apps/hubic-gtk.svg
	install -D -m644 data/${ICON_THEME}/hubic-gtk-alert.svg $(DEST)/share/icons/hicolor/scalable/status/hubic-gtk-alert.svg
	install -D -m644 data/${ICON_THEME}/hubic-gtk-busy.svg  $(DEST)/share/icons/hicolor/scalable/status/hubic-gtk-busy.svg

install-lang:
	for lang in $(L10N) ; do \
	  install -d -m755 $(DEST)/share/locale/$$lang/LC_MESSAGES ; \
	  msgfmt -o $(DEST)/share/locale/$$lang/LC_MESSAGES/hubic-gtk.mo po/$$lang/LC_MESSAGES/hubic-gtk.po ; \
	done

uninstall:
	rm $(DEST)/bin/$(PKGNAME)
	rm $(DEST)/share/icons/gnome/scalable/apps/hubic-gtk.svg
	rm $(DEST)/share/icons/gnome/scalable/status/hubic-gtk-alert.svg
	rm $(DEST)/share/icons/gnome/scalable/status/hubic-gtk-busy.svg
	rm $(DEST)/share/icons/hicolor/scalable/apps/hubic-gtk.svg
	rm $(DEST)/share/icons/hicolor/scalable/status/hubic-gtk-alert.svg
	rm $(DEST)/share/icons/hicolor/scalable/status/hubic-gtk-busy.svg
	rm $(DEST)/share/applications/$(PKGNAME).desktop
	rm $(DEST)/share/licenses/$(PKGNAME)/LICENSE
	rmdir $(DEST)/share/licenses/$(PKGNAME)

	for lang in $(L10N) ; do \
	  rm $(DEST)/share/locale/$$lang/LC_MESSAGES/hubic-gtk.mo ; \
	done

clean:
	rm $(PKGNAME)
