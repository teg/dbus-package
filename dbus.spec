%define gettext_package dbus

%define expat_version           1.95.5
%define glib2_version           2.2.0
%define qt_version              3.1.0

%define dbus_user_uid           81

Summary: D-BUS message bus
Name: dbus
Version: 0.13
Release: 6
URL: http://www.freedesktop.org/software/dbus/
Source0: %{name}-%{version}.tar.gz
License: AFL/GPL
Group: System Environment/Libraries
BuildRoot: %{_tmppath}/%{name}-root
PreReq: chkconfig
BuildRequires: expat-devel >= %{expat_version}
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: qt-devel    >= %{qt_version}

Patch1: dbus-0.13-uid.patch

%description

D-BUS is a system for sending messages between applications. It is
used both for the systemwide message bus service, and as a
per-user-login-session messaging facility.

%package devel
Summary: Libraries and headers for D-BUS
Group: Development/Libraries
Requires: %name = %{version}-%{release}

%description devel

Headers and static libraries for D-BUS.

%package glib
Summary: GLib-based library for using D-BUS
Group: Development/Libraries
Requires: %name = %{version}-%{release}

%description glib

D-BUS add-on library to integrate the standard D-BUS library with
the GLib thread abstraction and main loop.

%if 0

%package qt
Summary: Qt-based library for using D-BUS
Group: Development/Libraries
Requires: %name = %{version}-%{release}

%description qt

D-BUS add-on library to integrate the standard D-BUS library with
the Qt thread abstraction and main loop.

%endif

%package x11
Summary: X11-requiring add-ons for D-BUS
Group: Development/Libraries
Requires: %name = %{version}-%{release}

%description x11

D-BUS contains some tools that require Xlib to be installed, those are
in this separate package so server systems need not install X.

%prep
%setup -q

%patch1 -p1 -b .uid

%build

COMMON_ARGS="--enable-glib=yes --enable-qt=no"

if test -d %{_libdir}/qt-3.1 ; then
   export QTDIR=%{_libdir}/qt-3.1
else
   echo "WARNING: %{_libdir}/qt-3.1 does not exist"
fi

#### Fix user to run the system bus as
perl -pi -e 's@<user>[a-z]+</user>@<user>%{dbus_user_uid}</user>@g' bus/system.conf*

### this is some crack because bits of dbus can be 
### smp-compiled but others don't feel like working
function make_fast() {
        ### try to burn through it with SMP a couple times
        make %{?_smp_mflags} || true
        make %{?_smp_mflags} || true
        ### then do a real make and don't ignore failure
        make
}

#### Build once with tests to make check
%configure $COMMON_ARGS --enable-tests=yes --enable-verbose-mode=yes --enable-asserts=yes
make_fast
DBUS_VERBOSE=1 make check > dbus-check.log 2>&1 || (cat dbus-check.log && false)

#### Clean up and build again 
make clean 

%configure $COMMON_ARGS --disable-tests --disable-verbose-mode --disable-asserts
make_fast

%install
rm -rf %{buildroot}

%makeinstall

rm -f $RPM_BUILD_ROOT%{_libdir}/*.la

## %find_lang %{gettext_package}

%clean
rm -rf %{buildroot}

%pre
# Add the "dbus" user
/usr/sbin/useradd -c 'System message bus' -u %{dbus_user_uid} \
	-s /sbin/nologin -r -d '/' dbus 2> /dev/null || :

%post
/sbin/ldconfig
/sbin/chkconfig --add messagebus

%preun
if [ $1 = 0 ]; then
    service messagebus stop > /dev/null 2>&1
    /sbin/chkconfig --del messagebus
fi

%postun
/sbin/ldconfig
if [ "$1" -ge "1" ]; then
  service messagebus condrestart > /dev/null 2>&1
fi

##  -f %{gettext_package}.lang
%files
%defattr(-,root,root)

%doc COPYING ChangeLog NEWS

%dir %{_sysconfdir}/dbus-1
%config %{_sysconfdir}/dbus-1/*.conf
%config %{_sysconfdir}/rc.d/init.d/*
%dir %{_sysconfdir}/dbus-1/system.d
%dir %{_localstatedir}/run/dbus
%dir %{_libdir}/dbus-1.0
%{_bindir}/dbus-daemon-1
%{_bindir}/dbus-monitor
%{_bindir}/dbus-send
%{_bindir}/dbus-cleanup-sockets
%{_libdir}/*dbus-1*.so.*
%{_datadir}/man/man*/*
%{_libdir}/dbus-1.0/services

%files devel
%defattr(-,root,root)

%{_libdir}/lib*.a
%{_libdir}/lib*.so
%{_libdir}/dbus-1.0/include
%{_libdir}/pkgconfig/*
%{_includedir}/*

%files glib
%defattr(-,root,root)

%{_libdir}/*glib*.so.*

%if 0
%files qt
%defattr(-,root,root)

%{_libdir}/*qt*.so.*

%endif

%files x11
%defattr(-,root,root)

%{_bindir}/dbus-launch

%changelog
* Thu Oct 16 2003 Havoc Pennington <hp@redhat.com> 0.13-6
- hmm, dbus doesn't support uids in the config file. fix.

* Thu Oct 16 2003 Havoc Pennington <hp@redhat.com> 0.13-5
- put uid instead of username in the config file, to keep things working with name change

* Thu Oct 16 2003 Havoc Pennington <hp@redhat.com> 0.13-4
- make subpackages require the specific release, not just version, of base package

* Thu Oct 16 2003 Havoc Pennington <hp@redhat.com> 0.13-3
- change system user "messagebus" -> "dbus" to be under 8 chars

* Mon Sep 29 2003 Havoc Pennington <hp@redhat.com> 0.13-2
- see if removing qt subpackage for now will get us through the build system,
  qt bindings not useful yet anyway

* Sun Sep 28 2003 Havoc Pennington <hp@redhat.com> 0.13-1
- 0.13 fixes a little security oops

* Mon Aug  4 2003 Havoc Pennington <hp@redhat.com> 0.11.91-3
- break the tiny dbus-launch that depends on X into separate package
  so a CUPS server doesn't need X installed

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Sat May 17 2003 Havoc Pennington <hp@redhat.com> 0.11.91-1
- 0.11.91 cvs snap properly merges system.d

* Fri May 16 2003 Havoc Pennington <hp@redhat.com> 0.11.90-1
- build a cvs snap with a few more fixes

* Fri May 16 2003 Havoc Pennington <hp@redhat.com> 0.11-2
- fix a crash that was breaking cups

* Thu May 15 2003 Havoc Pennington <hp@redhat.com> 0.11-1
- 0.11

* Thu May 15 2003 Havoc Pennington <hp@redhat.com> 0.10.90-1
- use rc.d/init.d not init.d, bug #90192
- include the new man pages

* Fri Apr 11 2003 Havoc Pennington <hp@redhat.com> 0.9-1
- 0.9
- export QTDIR explicitly
- re-enable qt, the problem was most likely D-BUS configure

* Tue Apr  1 2003 Havoc Pennington <hp@redhat.com> 0.6.94-1
- update from CVS with a fix to set uid after gid

* Tue Apr  1 2003 Havoc Pennington <hp@redhat.com> 0.6.93-1
- new cvs snap that actually forks to background and changes 
  user it's running as and so forth
- create our system user in pre

* Mon Mar 31 2003 Havoc Pennington <hp@redhat.com> 0.6.92-1
- fix for "make check" test that required a home directory

* Mon Mar 31 2003 Havoc Pennington <hp@redhat.com> 0.6.91-1
- disable qt for now because beehive hates me
- pull a slightly newer cvs snap that creates socket directory
- cat the make check log after make check fails

* Mon Mar 31 2003 Havoc Pennington <hp@redhat.com> 0.6.90-1
- initial build

