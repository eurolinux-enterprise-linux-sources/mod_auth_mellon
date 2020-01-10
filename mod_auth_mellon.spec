Summary: A SAML 2.0 authentication module for the Apache Httpd Server
Name: mod_auth_mellon
Version: 0.14.0
Release: 2%{?dist}.4
Group: System Environment/Daemons
Source0: https://github.com/UNINETT/mod_auth_mellon/releases/download/v%{version}/%{name}-%{version}.tar.gz
Source1: auth_mellon.conf
Source2: 10-auth_mellon.conf
Source3: mod_auth_mellon.conf
Source4: mellon_create_metadata.sh
Source5: README.redhat.rst
Source6: mellon_user_guide.html
License: GPLv2+
BuildRequires: curl-devel
BuildRequires: glib2-devel
BuildRequires: httpd-devel
BuildRequires: lasso-devel >= 2.5.1
BuildRequires: openssl-devel
BuildRequires: xmlsec1-devel
Requires: httpd-mmn = %{_httpd_mmn}
Requires: lasso >= 2.5.1
Url: https://github.com/UNINETT/mod_auth_mellon

Patch0001: 0001-Modify-am_handler-setup-to-run-before-mod_proxy.patch
Patch0002: 0002-Fix-redirect-URL-validation-bypass.patch

# FIXME: RHEL-7 does not have rubygem-asciidoctor, only asciidoc. However,
# I could not get asciidoc to render properly so instead I generated
# mellon_user_guide.html on Fedora using asciidoctor and included
# mellon_user_guide.html as a SOURCE. If the user guide source is updated
# the mellon_user_guide.html will need to be regenerated. 

%description
The mod_auth_mellon module is an authentication service that implements the
SAML 2.0 federation protocol. It grants access based on the attributes
received in assertions generated by a IdP server.

%prep
%setup -q -n %{name}-%{version}
%patch1 -p1
%patch2 -p1

%build
export APXS=%{_httpd_apxs}
%configure --enable-diagnostics
make clean
make %{?_smp_mflags}
cp .libs/%{name}.so %{name}-diagnostics.so

%configure
make clean
make %{?_smp_mflags}

%install
# install module
mkdir -p %{buildroot}%{_httpd_moddir}
install -m 755 .libs/%{name}.so %{buildroot}%{_httpd_moddir}
install -m 755 %{name}-diagnostics.so %{buildroot}%{_httpd_moddir}

# install module configuration
mkdir -p %{buildroot}%{_httpd_confdir}
install -m 644 %{SOURCE1} %{buildroot}%{_httpd_confdir}
mkdir -p %{buildroot}%{_httpd_modconfdir}
install -m 644 %{SOURCE2} %{buildroot}%{_httpd_modconfdir}

mkdir -p %{buildroot}%{_tmpfilesdir}
install -m 644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}
mkdir -p %{buildroot}/run/%{name}

# install script to generate metadata
mkdir -p %{buildroot}/%{_libexecdir}/%{name}
install -m 755 %{SOURCE4} %{buildroot}/%{_libexecdir}/%{name}

#install documentation
mkdir -p %{buildroot}/%{_pkgdocdir}

# install Red Hat README
install -m 644 %{SOURCE5} %{buildroot}/%{_pkgdocdir}

# install user guide
cp -r doc/user_guide %{buildroot}/%{_pkgdocdir}
install -m 644 %{SOURCE6} %{buildroot}/%{_pkgdocdir}/user_guide

%package diagnostics
Summary: Build of mod_auth_mellon with diagnostic logging
Requires: %{name} = %{version}-%{release}

%description diagnostics
Build of mod_auth_mellon with diagnostic logging. See README.redhat.rst
in the doc directory for instructions on using the diagnostics build.

%files diagnostics
%{_httpd_moddir}/%{name}-diagnostics.so

%files
%defattr(-,root,root)
%if 0%{?rhel} && 0%{?rhel} < 7
%doc COPYING
%else
%license COPYING
%endif
%doc README.md NEWS ECP.rst
%doc %{_pkgdocdir}/README.redhat.rst
%doc %{_pkgdocdir}/user_guide
%config(noreplace) %{_httpd_modconfdir}/10-auth_mellon.conf
%config(noreplace) %{_httpd_confdir}/auth_mellon.conf
%{_httpd_moddir}/mod_auth_mellon.so
%{_tmpfilesdir}/mod_auth_mellon.conf
%{_libexecdir}/%{name}
%dir /run/%{name}/

%changelog
* Mon Apr  8 2019 Jakub Hrozek <jhrozek@redhat.com> - 0.14.0-2.4
- Actually apply the patch in the previous build
- Resolves: rhbz#1697488 - CVE-2019-3877 mod_auth_mellon: open redirect
                           in logout url when using URLs with backslashes

* Mon Apr  8 2019 Jakub Hrozek <jhrozek@redhat.com> - 0.14.0-2.3
- Resolves: rhbz#1697488 - CVE-2019-3877 mod_auth_mellon: open redirect
                           in logout url when using URLs with backslashes
                           [rhel-7] [rhel-7.6.z]

* Mon Apr  8 2019 Jakub Hrozek <jhrozek@redhat.com> - 0.14.0-2.2
- Resolves: rhbz#1697487 - mod_auth_mellon Cert files name wrong when
                           hostname contains a number

* Fri Mar 22 2019 Jakub Hrozek <jhrozek@redhat.com> - 0.14.0-2.1
- Resolves: rhbz#1692455 - CVE-2019-3878 mod_auth_mellon: authentication
                           bypass in ECP flow [rhel-7.6.z]

* Fri Jun  1 2018  <jdennis@redhat.com> - 0.14.0-2
- Resolves: rhbz#1553885
- fix file permissions on doc files

* Fri Jun  1 2018  <jdennis@redhat.com> - 0.14.0-1
- Resolves: rhbz#1553885
- Rebase to current upstream release

* Thu Mar 29 2018 John Dennis <jdennis@redhat.com> - 0.13.1-2
- Resolves: rhbz#1481330 Add diagnostic logging
- Resolves: rhbz#1295472 Add MellonSignatureMethod config option to set
  signature method used to sign SAML messages sent by Mellon.
  Defaults to original sha1.

* Fri Oct 20 2017 John Dennis <jdennis@redhat.com> - 0.13.1-1
- Resolves: rhbz#1481332 Upgrade to current upstream 0.13.1
- Adds the following upstream bug fixes on top of 0.13.1:
  * ee97812 Add Mellon User Guide
  * daa5d1e If no IdP's are defined explicitly log that fact
  * c291232 Make MellonUser case-insensitive.
  * 2c2e19d Fix incorrect error check for many `lasso_*`-functions.
  * 5c5ed1d Fix segmentation fault with POST field without a value.
  * 4c924d9 Fix some log message typos
  * 93faba4 Update log msg for Invalid Destination and Invalid Audience to
    show both the expected and received values.
- Add new mellon user guide to installed docdir

* Mon Jan 30 2017 John Dennis <jdennis@redhat.com> - 0.11.0-4
- Resolves: rhbz#1414021 - Incorrect Content-Type header in ECP PAOS
  Rebuilding due to missing comment in Changelog

* Mon Jan 30 2017 John Dennis <jdennis@redhat.com> - 0.11.0-3
- Resolves: rhbz#1414021 - Incorrect Content-Type header in ECP PAOS

* Fri Apr  8 2016 John Dennis <jdennis@redhat.com> - 0.11.0-2
- Resolves: bug #1296286
  mod_auth_mellon emits CRITICAL warning message in Apache log when doing ECP
- Resolves: bug #1324536
  Installing mod_auth_mellon causes working Kerberos authentication
  to start failing
- Add ECP.rst documentation file that was erroneously omitted

* Fri Sep 18 2015 John Dennis <jdennis@redhat.com> - 0.11.0-1
- Upgrade to upstream 0.11.0 release.
- Includes ECP support, see NEWS for all changes.
- Update mellon_create_metadata.sh to match internally generated metadata,
  includes AssertionConsumerService for postResponse, artifactResponse &
  paosResponse.
- Add lasso 2.5.0 version dependency
- Resolves: #1205345

* Mon Aug 24 2015 John Dennis <jdennis@redhat.com> - 0.10.0-3
- Rebase to upstream 0.10.0 release
- Apply upstream commits post 0.10.0 release
- Apply revised ECP pending patches,
  fix patch to pickup change in configure script that causes
  HAVE_ECP to be defined
- Resolves: #1205345

* Wed Aug 19 2015 John Dennis <jdennis@redhat.com> - 0.10.0-2
- Rebase to upstream 0.10.0 release
- Apply upstream commits post 0.10.0 release
- Apply revised ECP pending patches
- Resolves: #1205345

* Mon Jun 22 2015 John Dennis <jdennis@redhat.com> - 0.10.0-1
- Rebase to upstream 0.10.0 release
- Apply upstream commits post 0.10.0 release
- Apply ECP pending patches
- Resolves: #1205345

* Mon Dec  8 2014 Simo Sorce <simo@redhat.com> 0.9.1-4
- Large scale intreop patches
- Resolves: #1167844

* Wed Sep 10 2014 Simo Sorce <simo@redhat.com> 0.9.1-3
- Fix upstream sources URL
- Related: #1120353

* Fri Sep  5 2014 Simo Sorce <simo@redhat.com> 0.9.1-2
- Import package in RHEL7
- Resolves: #1120353

* Tue Sep  2 2014 Simo Sorce <simo@redhat.com> 0.9.1-1
- New upstream release

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jun 24 2014 Simo Sorce <simo@redhat.com> 0.8.0-1
- New upstream realease version 0.8.0
- Upstream moved to github
- Drops patches as they have been all included upstream

* Fri Jun 20 2014 Simo Sorce <simo@redhat.com> 0.7.0-3
- Backport of useful patches from upstream
  - Better handling of IDP reported errors
  - Better handling of session data storage size

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Dec 10 2013 Simo Sorce <simo@redhat.com> 0.7.0-1
- Fix ownership of /run files

* Wed Nov 27 2013 Simo Sorce <simo@redhat.com> 0.7.0-0
- Initial Fedora release based on version 0.7.0
- Based on an old spec file by Jean-Marc Liger <jmliger@siris.sorbonne.fr>
