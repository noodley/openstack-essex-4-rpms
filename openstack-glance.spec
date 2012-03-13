#
# This is 2012.1 essex-4 rc1 release
#
%global release_name essex
%global release_letter e
%global milestone 4
%global snapdate 20120312
%global git_revno 1323
%global snaptag ~%{release_letter}%{milestone}~%{snapdate}.%{git_revno}


Name:             openstack-glance
Version:          2012.1
Release:          0.2.rc1.%{release_letter}%{milestone}%{?dist}
Summary:          OpenStack Image Service

Group:            Applications/System
License:          ASL 2.0
URL:              http://glance.openstack.org
Source0:          http://glance.openstack.org/tarballs/glance-2012.1~rc1~%{snapdate}.%{git_revno}.tar.gz
Source1:          glance-api.init
Source2:          glance-registry.init
Source3:          openstack-glance.logrotate

#
# patches_base=essex-4
#
Patch0001: 0001-Don-t-access-the-net-while-building-docs.patch

BuildArch:        noarch
BuildRequires:    python2-devel
BuildRequires:    python-setuptools
BuildRequires:    python-distutils-extra
BuildRequires:    intltool

Requires(post):   chkconfig
Requires(postun): initscripts
Requires(preun):  chkconfig
Requires(pre):    shadow-utils
Requires:         python-glance = %{version}-%{release}

%description
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images. The Image Service API server
provides a standard REST interface for querying information about virtual disk
images stored in a variety of back-end stores, including OpenStack Object
Storage. Clients can register new virtual disk images with the Image Service,
query for information on publicly available disk images, and use the Image
Service's client library for streaming virtual disk images.

This package contains the API and registry servers.

%package -n       python-glance
Summary:          Glance Python libraries
Group:            Applications/System

Requires:         pysendfile
Requires:         python-eventlet
Requires:         python-httplib2
Requires:         python-iso8601
Requires:         python-kombu
Requires:         python-migrate
Requires:         python-paste-deploy
Requires:         python-routes
Requires:         python-sqlalchemy
Requires:         python-webob
Requires:         python-crypto
Requires:         pyxattr

%description -n   python-glance
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images.

This package contains the glance Python library.

%package doc
Summary:          Documentation for OpenStack Image Service
Group:            Documentation

Requires:         %{name} = %{version}-%{release}

#BuildRequires:    systemd-units
BuildRequires:    python-sphinx
BuildRequires:    graphviz

# Required to build module documents
BuildRequires:    python-boto
BuildRequires:    python-daemon
BuildRequires:    python-eventlet
BuildRequires:    python-gflags
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy
BuildRequires:    python-webob

%description      doc
OpenStack Image Service (code-named Glance) provides discovery, registration,
and delivery services for virtual disk images.

This package contains documentation files for glance.

%prep
%setup -q -n glance-%{version}

%patch0001 -p1

sed -i 's|\(sql_connection = sqlite:///\)\(glance.sqlite\)|\1%{_sharedstatedir}/glance/\2|' etc/glance-registry.conf

sed -i '/\/usr\/bin\/env python/d' glance/common/config.py glance/registry/db/migrate_repo/manage.py

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests

export PYTHONPATH="$( pwd ):$PYTHONPATH"
pushd doc
sphinx-build -b html source build/html
sphinx-build -b man source build/man

mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 build/man/*.1 %{buildroot}%{_mandir}/man1/
popd

# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
rm -f %{buildroot}%{_sysconfdir}/glance*.conf
rm -f %{buildroot}%{_sysconfdir}/glance*.ini
rm -f %{buildroot}%{_sysconfdir}/logging.cnf.sample
rm -f %{buildroot}%{_sysconfdir}/policy.json
rm -f %{buildroot}/usr/share/doc/glance/README.rst

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/glance/images

# Config file
install -p -D -m 644 etc/glance-api.conf %{buildroot}%{_sysconfdir}/glance/glance-api.conf
install -p -D -m 644 etc/glance-api-paste.ini %{buildroot}%{_sysconfdir}/glance/glance-api-paste.ini
install -p -D -m 644 etc/glance-registry.conf %{buildroot}%{_sysconfdir}/glance/glance-registry.conf
install -p -D -m 644 etc/glance-registry-paste.ini %{buildroot}%{_sysconfdir}/glance/glance-registry-paste.ini
install -p -D -m 644 etc/policy.json %{buildroot}%{_sysconfdir}/glance/policy.json

# Initscripts
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_initrddir}/glance-api
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_initrddir}/glance-registry

# Logrotate config
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-glance

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/glance

# Install log directory
install -d -m 755 %{buildroot}%{_localstatedir}/log/glance

%pre
getent group glance >/dev/null || groupadd -r glance -g 161
getent passwd glance >/dev/null || \
useradd -u 161 -r -g glance -d %{_sharedstatedir}/glance -s /sbin/nologin \
-c "OpenStack Glance Daemons" glance
exit 0

%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /sbin/chkconfig --add glance-api >/dev/null 2>&1
    /sbin/chkconfig --add glance-registry >/dev/null 2>&1
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /sbin/chkconfig --del glance-api >/dev/null 2>&1
    /sbin/chkconfig --del glance-registry >/dev/null 2>&1
    /etc/init.d/glance-api stop >/dev/null 2>&1 
    /etc/init.d/glance-registry stop >/dev/null 2>&1 
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /etc/init.d/glance-api restart >/dev/null 2>&1 
    /etc/init.d/glance-registry restart >/dev/null 2>&1 
fi

%files
%doc README.rst
%{_bindir}/glance
%{_bindir}/glance-api
%{_bindir}/glance-control
%{_bindir}/glance-manage
%{_bindir}/glance-registry
%{_bindir}/glance-cache-cleaner
%{_bindir}/glance-cache-manage
%{_bindir}/glance-cache-prefetcher
%{_bindir}/glance-cache-pruner
%{_bindir}/glance-cache-queue-image
%{_bindir}/glance-scrubber
%{_initrddir}/glance-api
%{_initrddir}/glance-registry
%{_mandir}/man1/glance*.1.gz
%dir %{_sysconfdir}/glance
%config(noreplace) %{_sysconfdir}/glance/glance-api.conf
%config(noreplace) %{_sysconfdir}/glance/glance-api-paste.ini
%config(noreplace) %{_sysconfdir}/glance/glance-registry.conf
%config(noreplace) %{_sysconfdir}/glance/glance-registry-paste.ini
%config(noreplace) %{_sysconfdir}/glance/policy.json
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-glance
%dir %attr(0755, glance, nobody) %{_sharedstatedir}/glance
%dir %attr(0755, glance, nobody) %{_localstatedir}/log/glance
%dir %attr(0755, glance, nobody) %{_localstatedir}/run/glance

%files -n python-glance
%doc README.rst
%{python_sitelib}/glance
%{python_sitelib}/glance-%{version}-*.egg-info

%files doc
%doc doc/build/html

%changelog
* Mon Mar 12 2012 Marco Sinhoreli <marco.sinhoreli@corp.globo.com> - 2012.1-rc1
- First release migrate from fedora-16 packages

