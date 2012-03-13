#
# This is 2012.1 essex-4 rc1 release
#

%global release_name essex
%global release_letter e
%global milestone 4
%global snapdate 20120312
%global git_revno 2123
%global snaptag ~%{release_letter}%{milestone}~%{snapdate}.%{git_revno}

Name:           openstack-keystone
Version:        2012.1
Release:        0.2.rc1%{release_letter}%{milestone}%{?dist}
Summary:        OpenStack Identity Service

License:        ASL 2.0
URL:            http://keystone.openstack.org/
#Source0:        http://launchpad.net/keystone/%{release_name}/%{release_name}-%{milestone}/+download/keystone-%{version}~%{release_letter}%{milestone}.tar.gz

Source0:        http://keystone.openstack.org/tarballs/keystone-2012.1~rc1~20120312.2123.tar.gz
Source1:        openstack-keystone.logrotate
Source2:        keystone.init
Source3:        openstack-keystone-db-setup
Source4:        openstack-config-set
Source5:        sample_data.sh

# https://review.openstack.org/4658
# https://review.openstack.org/5049
Patch1:         sample_data.sh-catalog-backend.patch
# https://review.openstack.org/4997
Patch2:         add-more-default-catalog-templates.patch

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-sphinx >= 1.0
BuildRequires:  python-iniparse
#BuildRequires:  systemd-units

Requires:       python-keystone = %{version}-%{release}
Requires:       python-keystoneclient >= 2012.1-0.4.e4

Requires(post):   chkconfig grep sudo libselinux-utils
Requires(postun): initscripts
Requires(preun):  chkconfig
Requires(pre):    shadow-utils

%description
Keystone is a Python implementation of the OpenStack
(http://www.openstack.org) identity service API.

This package contains the Keystone daemon.

%package -n       python-keystone
Summary:          Keystone Python libraries
Group:            Applications/System
# python-keystone added in 2012.1-0.2.e3
Conflicts:      openstack-keystone < 2012.1-0.2.e3

Requires:       python-crypto
Requires:       python-dateutil
Requires:       python-eventlet
Requires:       python-httplib2
Requires:       python-ldap
Requires:       python-lxml
Requires:       python-memcached
Requires:       python-migrate
Requires:       python-paste
Requires:       python-paste-deploy
Requires:       python-paste-script
Requires:       python-prettytable
Requires:       python-routes
Requires:       python-sqlalchemy
Requires:       python-webob
Requires:       python-passlib
Requires:       MySQL-python

%description -n   python-keystone
Keystone is a Python implementation of the OpenStack
(http://www.openstack.org) identity service API.

This package contains the Keystone Python library.

%prep
%setup -q -n keystone-%{version}
#%patch1 -p1
#%patch2 -p1

# change default configuration
%{SOURCE4} etc/keystone.conf DEFAULT log_file %{_localstatedir}/log/keystone/keystone.log
%{SOURCE4} etc/keystone.conf sql connection mysql://keystone:keystone@localhost/keystone
%{SOURCE4} etc/keystone.conf catalog template_file %{_sysconfdir}/keystone/default_catalog.templates
%{SOURCE4} etc/keystone.conf catalog driver keystone.catalog.backends.sql.Catalog
%{SOURCE4} etc/keystone.conf identity driver keystone.identity.backends.sql.Identity
%{SOURCE4} etc/keystone.conf token driver keystone.token.backends.sql.Token
%{SOURCE4} etc/keystone.conf ec2 driver keystone.contrib.ec2.backends.sql.Ec2

find . \( -name .gitignore -o -name .placeholder \) -delete
find keystone -name \*.py -exec sed -i '/\/usr\/bin\/env python/d' {} \;


%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root %{buildroot}

# Delete tests
rm -fr %{buildroot}%{python_sitelib}/tests
rm -fr %{buildroot}%{python_sitelib}/run_tests.*

install -d -m 755 %{buildroot}%{_sysconfdir}/keystone
install -p -D -m 640 etc/keystone.conf %{buildroot}%{_sysconfdir}/keystone/keystone.conf
install -p -D -m 640 etc/default_catalog.templates %{buildroot}%{_sysconfdir}/keystone/default_catalog.templates
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-keystone
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_initrddir}/keystone
# Install database setup helper script.
install -p -D -m 755 %{SOURCE3} %{buildroot}%{_bindir}/openstack-keystone-db-setup
# Install sample data script.
install -p -D -m 755 %{SOURCE5} %{buildroot}%{_bindir}/openstack-keystone-sample-data
# Install configuration helper script.
install -p -D -m 755 %{SOURCE4} %{buildroot}%{_bindir}/openstack-config-set

install -d -m 755 %{buildroot}%{_sharedstatedir}/keystone
install -d -m 755 %{buildroot}%{_localstatedir}/log/keystone

# docs generation requires everything to be installed first
export PYTHONPATH="$( pwd ):$PYTHONPATH"
pushd doc
make html SPHINXAPIDOC=echo
popd
# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees docs/build/html/.buildinfo

%pre
getent group keystone >/dev/null || groupadd -r keystone
getent passwd keystone >/dev/null || \
useradd -r -g keystone -d %{_sharedstatedir}/keystone -s /sbin/nologin \
-c "OpenStack Keystone Daemons" keystone
exit 0

%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /sbin/chkconfig --add keystone >/dev/null 2>&1
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /sbin/chkconfig --del keystone >/dev/null 2>&1
    /etc/init.d/keystone stop >/dev/null 2>&1 
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /etc/init.d/keystone restart >/dev/null 2>&1 
fi

%files
%doc LICENSE
%doc README.rst
%doc doc/build/html
%{_bindir}/keystone-all
%{_bindir}/keystone-manage
%{_bindir}/openstack-config-set
%{_bindir}/openstack-keystone-db-setup
%{_bindir}/openstack-keystone-sample-data
%{_initrddir}/keystone
%dir %{_sysconfdir}/keystone
%config(noreplace) %attr(640, root, keystone) %{_sysconfdir}/keystone/keystone.conf
%config(noreplace) %attr(640, root, keystone) %{_sysconfdir}/keystone/default_catalog.templates
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-keystone
%dir %attr(-, keystone, keystone) %{_sharedstatedir}/keystone
%dir %attr(-, keystone, keystone) %{_localstatedir}/log/keystone

%files -n python-keystone
%defattr(-,root,root,-)
%doc LICENSE
%{python_sitelib}/keystone
%{python_sitelib}/keystone-%{version}-*.egg-info

%changelog
* Mon Mar 12 2012 Marco Sinhoreli <marco.sinhoreli@corp.globo.com> - 2012.1-0.1.e4
- First release migrate from fedora-16 packages
