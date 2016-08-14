DEST=/usr
L10N=fr en_US
PKGNAME=hubic-gtk
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

	install -D -m755 $(PKGNAME)          $(DEST)/bin/$(PKGNAME)
	install -D -m644 hubic-gtk.svg       $(DEST)/share/icons/gnome/scalable/apps/hubic-gtk.svg
	install -D -m644 hubic-gtk-alert.svg $(DEST)/share/icons/gnome/scalable/status/hubic-gtk-alert.svg
	install -D -m644 hubic-gtk-busy.svg  $(DEST)/share/icons/gnome/scalable/status/hubic-gtk-busy.svg
	install -D -m644 hubic-gtk.svg       $(DEST)/share/icons/hicolor/scalable/apps/hubic-gtk.svg
	install -D -m644 hubic-gtk-alert.svg $(DEST)/share/icons/hicolor/scalable/status/hubic-gtk-alert.svg
	install -D -m644 hubic-gtk-busy.svg  $(DEST)/share/icons/hicolor/scalable/status/hubic-gtk-busy.svg
	install -D -m644 $(PKGNAME).desktop  $(DEST)/share/applications
	install -D -m644 LICENSE             $(DEST)/share/licenses/$(PKGNAME)/LICENSE

install-lang:
	for lang in $(L10N) ; do \
	  install -d -m755 $(DEST)/share/locale/$$lang/LC_MESSAGES ; \
	  msgfmt -o $(DEST)/share/locale/$$lang/LC_MESSAGES/hubic-gtk.mo	po/$$lang/LC_MESSAGES/hubic-gtk.po ; \
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


OLDVER != sed -n "s/pkgver=\([\d.]*\)/\1/p" archlinux/PKGBUILD
OLDREL != sed -n "s/pkgrel=\(\d*\)/\1/p" archlinux/PKGBUILD
ifeq ($(OLDVER), $(PKGVER))
	PKGREL != expr $(OLDREL) + 1
else
	PKGREL = 1
endif

dist: sha1sum
	sed -i "s/pkgver=.*/pkgver=$(PKGVER)/" archlinux/PKGBUILD ; \
	sed -i "s/pkgrel=.*/pkgrel=$(PKGREL)/" archlinux/PKGBUILD

sha1sum: SHA1SUM = $(shell sha1sum archlinux/$(PKGNAME)-$(PKGVER).tar.gz | cut -d' ' -f1)
sha1sum: $(PKGNAME)-$(PKGVER).tar.gz
	sed -i "s/_fossilver=.*/_fossilver=$(shell echo $(SHA1SUM) | cut -c1-10)/" archlinux/PKGBUILD
	sed -i "s/sha1sums=.*/sha1sums=('$(SHA1SUM)')/" archlinux/PKGBUILD

$(PKGNAME)-$(PKGVER).tar.gz:
	cd ../ ; tar czf $(PKGNAME)-$(PKGVER).tar.gz hubic-gtk --exclude archlinux ; mv $(PKGNAME)-$(PKGVER).tar.gz hubic-gtk/archlinux/

clean:
	rm $(PKGNAME)
