DEST=/usr
L10N=fr en_US
PKGNAME=hubic-gtk
#PKGVER=dev

all: build install

build:
	cp $(PKGNAME).py $(PKGNAME)
	sed -i "s|HUBIC_ICONS_PATH = os.path.dirname(os.path.realpath(__file__))|HUBIC_ICONS_PATH = '$(DEST)/share/icons/hicolor/16x16/status'|" $(PKGNAME)
	sed -i "s|HUBIC_L10N_PATH = './po'|HUBIC_L10N_PATH = '$(DEST)/share/locale'|" $(PKGNAME)
	sed -i "s|HUBIC_STATUS_VERSION = 'dev'|HUBIC_STATUS_VERSION = '$(PKGVER)'|" $(PKGNAME)

install: install-bin install-lang

install-bin:
	install -d -m755	$(DEST)/bin
	install -d -m755	$(DEST)/share/applications
	install -d -m755	$(DEST)/share/licenses/$(PKGNAME)
	install -d -m755	$(DEST)/share/icons/hicolor/16x16/status

	install -D -m755 $(PKGNAME)         $(DEST)/bin/$(PKGNAME)
	install -D -m644 hubic_busy.png     $(DEST)/share/icons/hicolor/16x16/status/hubic_busy.png
	install -D -m644 hubic_error.png    $(DEST)/share/icons/hicolor/16x16/status/hubic_error.png
	install -D -m644 $(PKGNAME).desktop $(DEST)/share/applications
	install -D -m644 LICENSE            $(DEST)/share/licenses/$(PKGNAME)/LICENSE

install-lang:
	for lang in $(L10N) ; do \
	  install -d -m755 $(DEST)/share/locale/$$lang/LC_MESSAGES ; \
	  msgfmt -o $(DEST)/share/locale/$$lang/LC_MESSAGES/hubic-gtk.mo	po/$$lang/LC_MESSAGES/hubic-gtk.po ; \
	done

uninstall:
	rm $(DEST)/bin/$(PKGNAME)
	rm $(DEST)/share/icons/hicolor/16x16/hubic_busy.png
	rm $(DEST)/share/icons/hicolor/16x16/hubic_error.png
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
