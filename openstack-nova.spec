%global with_doc %{!?_without_doc:1}%{?_without_doc:0}

Name:             openstack-nova
Version:          2012.1
# The Release is in form 0.X.tag as per:
#   http://fedoraproject.org/wiki/Packaging:NamingGuidelines#Pre-Release_packages
# So for prereleases always increment X
Release:          0.2.rc1.e4%{?dist}
Summary:          OpenStack Compute (nova)

Group:            Applications/System
License:          ASL 2.0
URL:              http://openstack.org/projects/compute/
Source0:          http://nova.openstack.org/tarballs/nova-2012.1~rc1~20120313.13350.tar.gz
Source1:          nova.conf
Source6:          nova.logrotate

Source10:         nova-api.init
Source11:         nova-cert.init
Source12:         nova-compute.init
Source13:         nova-network.init
Source14:         nova-objectstore.init
Source15:         nova-scheduler.init
Source16:         nova-volume.init
Source17:         nova-direct-api.init
Source18:         nova-ajax-console-proxy.init
Source19:         nova-vncproxy.init

Source20:         nova-sudoers
Source21:         nova-polkit.pkla
Source22:         nova-ifc-template
Source23:         openstack-nova-db-setup

#
# patches_base=essex-4
#
Patch0001: 0001-Ensure-we-don-t-access-the-net-when-building-docs.patch
Patch0002: 0002-Add-VIF-and-interface-drivers-for-the-Linux-Bridge-p.patch
Patch0003: 0003-Adds-soft-reboot-support-to-libvirt.patch
Patch0004: 0004-Allows-new-style-config-to-be-used-for-flagfile.patch

BuildArch:        noarch
BuildRequires:    intltool
BuildRequires:    python-setuptools
BuildRequires:    python-distutils-extra >= 2.18
BuildRequires:    python-netaddr
BuildRequires:    python-lockfile

Requires:         python-nova = %{version}-%{release}

Requires:         python-paste
Requires:         python-paste-deploy

Requires:         bridge-utils
Requires:         dnsmasq
Requires:         libguestfs-mount >= 1.7.17
# The fuse dependency should be added to libguestfs-mount
Requires:         fuse
Requires:         libvirt-python
Requires:         libvirt >= 0.8.7
Requires:         libxml2-python
Requires:         python-cheetah
Requires:         MySQL-python

Requires:         euca2ools
Requires:         openssl
Requires:         sudo

Requires(post):   chkconfig grep sudo libselinux-utils
Requires(postun): initscripts
Requires(preun):  chkconfig
Requires(pre):    shadow-utils qemu-kvm

%description
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform. It gives you the
software, control panels, and APIs required to orchestrate a cloud,
including running instances, managing networks, and controlling access
through users and projects. OpenStack Compute strives to be both
hardware and hypervisor agnostic, currently supporting a variety of
standard hardware configurations and seven major hypervisors.

%package -n       python-nova
Summary:          Nova Python libraries
Group:            Applications/System

Requires:         vconfig
Requires:         PyXML
Requires:         curl
Requires:         m2crypto
Requires:         libvirt-python
Requires:         python-anyjson
Requires:         python-IPy
Requires:         python-boto
# TODO: make these messaging libs optional
Requires:         python-qpid
Requires:         python-carrot
Requires:         python-kombu
Requires:         python-amqplib
Requires:         python-daemon
Requires:         python-eventlet
Requires:         python-greenlet
Requires:         python-gflags
Requires:         python-iso8601
Requires:         python-lockfile
Requires:         python-lxml
Requires:         python-mox
Requires:         python-redis
Requires:         python-routes
Requires:         python-sqlalchemy
Requires:         python-tornado
Requires:         python-twisted-core
Requires:         python-twisted-web
Requires:         python-webob
Requires:         python-netaddr
# TODO: remove the following dependency which is minimal
Requires:         python-glance
Requires:         python-novaclient
Requires:         python-paste-deploy
Requires:         python-migrate
Requires:         python-ldap
Requires:         radvd
Requires:         iptables iptables-ipv6
Requires:         iscsi-initiator-utils
Requires:         scsi-target-utils
Requires:         lvm2
Requires:         socat
Requires:         coreutils

%description -n   python-nova
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform.

This package contains the nova Python library.

%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Compute
Group:            Documentation

Requires:         %{name} = %{version}-%{release}

#BuildRequires:    systemd-units
BuildRequires:    python-sphinx
BuildRequires:    graphviz
BuildRequires:    python-distutils-extra

BuildRequires:    python-nose
# Required to build module documents
BuildRequires:    python-IPy
BuildRequires:    python-boto
BuildRequires:    python-eventlet
BuildRequires:    python-gflags
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy
BuildRequires:    python-tornado
BuildRequires:    python-twisted-core
BuildRequires:    python-twisted-web
BuildRequires:    python-webob
# while not strictly required, quiets the build down when building docs.
BuildRequires:    python-carrot, python-mox, python-suds, m2crypto, bpython, python-memcached, python-migrate, python-iso8601

%description      doc
OpenStack Compute (codename Nova) is open source software designed to
provision and manage large networks of virtual machines, creating a
redundant and scalable cloud computing platform.

This package contains documentation files for nova.
%endif

%prep
%setup -q -n nova-%{version}

#%patch0001 -p1
#%patch0002 -p1
#%patch0003 -p1
#%patch0004 -p1

find . \( -name .gitignore -o -name .placeholder \) -delete

find nova -name \*.py -exec sed -i '/\/usr\/bin\/env python/d' {} \;

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# docs generation requires everything to be installed first
export PYTHONPATH="$( pwd ):$PYTHONPATH"
pushd doc
# Manually auto-generate to work around sphinx-build segfault
./generate_autodoc_index.sh
SPHINX_DEBUG=1 sphinx-build -b man source build/man
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 build/man/*.1 %{buildroot}%{_mandir}/man1/

%if 0%{?with_doc}
SPHINX_DEBUG=1 sphinx-build -b html source build/html
# Fix hidden-file-or-dir warnings
rm -fr build/html/.doctrees build/html/.buildinfo
%endif
popd

# Give stack, instance-usage-audit and clear_rabbit_queues a reasonable prefix
mv %{buildroot}%{_bindir}/stack %{buildroot}%{_bindir}/nova-stack
mv %{buildroot}%{_bindir}/instance-usage-audit %{buildroot}%{_bindir}/nova-instance-usage-audit
mv %{buildroot}%{_bindir}/clear_rabbit_queues %{buildroot}%{_bindir}/nova-clear-rabbit-queues

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/buckets
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/images
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/instances
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/keys
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/networks
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/tmp
install -d -m 755 %{buildroot}%{_localstatedir}/log/nova

# Setup ghost CA cert
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/CA
install -p -m 755 nova/CA/*.sh %{buildroot}%{_sharedstatedir}/nova/CA
install -p -m 644 nova/CA/openssl.cnf.tmpl %{buildroot}%{_sharedstatedir}/nova/CA
install -d -m 755 %{buildroot}%{_sharedstatedir}/nova/CA/{certs,crl,newcerts,projects,reqs}
touch %{buildroot}%{_sharedstatedir}/nova/CA/{cacert.pem,crl.pem,index.txt,openssl.cnf,serial}
install -d -m 750 %{buildroot}%{_sharedstatedir}/nova/CA/private
touch %{buildroot}%{_sharedstatedir}/nova/CA/private/cakey.pem

# Install config files
install -d -m 755 %{buildroot}%{_sysconfdir}/nova
install -p -D -m 640 %{SOURCE1} %{buildroot}%{_sysconfdir}/nova/nova.conf
install -p -D -m 640 etc/nova/api-paste.ini %{buildroot}%{_sysconfdir}/nova/api-paste.ini
install -p -D -m 640 etc/nova/policy.json %{buildroot}%{_sysconfdir}/nova/policy.json

# Install initscripts for Nova services _initrddir
install -p -D -m 755 %{SOURCE10} %{buildroot}%{_initrddir}/nova-api
install -p -D -m 755 %{SOURCE11} %{buildroot}%{_initrddir}/nova-cert
install -p -D -m 755 %{SOURCE12} %{buildroot}%{_initrddir}/nova-compute
install -p -D -m 755 %{SOURCE13} %{buildroot}%{_initrddir}/nova-network
install -p -D -m 755 %{SOURCE14} %{buildroot}%{_initrddir}/nova-objectstore
install -p -D -m 755 %{SOURCE15} %{buildroot}%{_initrddir}/nova-scheduler
install -p -D -m 755 %{SOURCE16} %{buildroot}%{_initrddir}/nova-volume
install -p -D -m 755 %{SOURCE17} %{buildroot}%{_initrddir}/nova-direct-api
install -p -D -m 755 %{SOURCE18} %{buildroot}%{_initrddir}/nova-ajax-console-proxy
install -p -D -m 755 %{SOURCE19} %{buildroot}%{_initrddir}/nova-vncproxy

# Install sudoers
install -p -D -m 440 %{SOURCE20} %{buildroot}%{_sysconfdir}/sudoers.d/nova

# Install logrotate
install -p -D -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-nova

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/nova

# Install template files
install -p -D -m 644 nova/auth/novarc.template %{buildroot}%{_datarootdir}/nova/novarc.template
install -p -D -m 644 nova/cloudpipe/client.ovpn.template %{buildroot}%{_datarootdir}/nova/client.ovpn.template
install -p -D -m 644 nova/virt/libvirt.xml.template %{buildroot}%{_datarootdir}/nova/libvirt.xml.template
install -p -D -m 644 nova/virt/interfaces.template %{buildroot}%{_datarootdir}/nova/interfaces.template
install -p -D -m 644 %{SOURCE22} %{buildroot}%{_datarootdir}/nova/interfaces.template

install -d -m 755 %{buildroot}%{_sysconfdir}/polkit-1/localauthority/50-local.d
install -p -D -m 644 %{SOURCE21} %{buildroot}%{_sysconfdir}/polkit-1/localauthority/50-local.d/50-nova.pkla

# Install database setup helper script.
install -p -D -m 755 %{SOURCE23} %{buildroot}%{_bindir}/openstack-nova-db-setup

# Remove ajaxterm and various other tools
rm -fr %{buildroot}%{_datarootdir}/nova/{ajaxterm,euca-get-ajax-console,install_venv.py,nova-debug,pip-requires,clean-vlans,with_venv.sh,esx}

# Remove unneeded in production stuff
rm -fr %{buildroot}%{python_sitelib}/run_tests.*
rm -f %{buildroot}%{_bindir}/nova-combined
rm -f %{buildroot}/usr/share/doc/nova/README*

%post
/sbin/chkconfig --add nova-${svc} >/dev/null 2>&1

%pre
getent group nova >/dev/null || groupadd -r nova --gid 162
if ! getent passwd nova >/dev/null; then
  useradd -u 162 -r -g nova -G nova,nobody,qemu -d %{_sharedstatedir}/nova -s /sbin/nologin -c "OpenStack Nova Daemons" nova
fi
# Add nova to the fuse group (if present) to support guestmount
if getent group fuse >/dev/null; then
  usermod -a -G fuse nova
fi
exit 0

%preun
if [ $1 -eq 0 ] ; then
    for svc in api cert compute network objectstore scheduler volume direct-api ajax-console-proxy vncproxy; do
    	/sbin/service nova-${svc} stop >/dev/null 2>&1
	/sbin/chkconfig --del nova-${svc} >/dev/null 2>&1
    done
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    for svc in api cert compute network objectstore scheduler volume direct-api ajax-console-proxy vncproxy; do
    	/sbin/service nova-${svc} restart >/dev/null 2>&1
    done
fi

%files
%doc LICENSE
%dir %{_sysconfdir}/nova
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/nova.conf
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/api-paste.ini
%config(noreplace) %attr(-, root, nova) %{_sysconfdir}/nova/policy.json
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-nova
%config(noreplace) %{_sysconfdir}/sudoers.d/nova
%config(noreplace) %{_sysconfdir}/polkit-1/localauthority/50-local.d/50-nova.pkla

%dir %attr(0755, nova, root) %{_localstatedir}/log/nova
%dir %attr(0755, nova, root) %{_localstatedir}/run/nova

%{_bindir}/nova-*
%{_bindir}/openstack-nova-db-setup
%{_initrddir}/nova-*
%{_datarootdir}/nova
%{_mandir}/man1/nova*.1.gz

%defattr(-, nova, nova, -)
%dir %{_sharedstatedir}/nova
%dir %{_sharedstatedir}/nova/buckets
%dir %{_sharedstatedir}/nova/images
%dir %{_sharedstatedir}/nova/instances
%dir %{_sharedstatedir}/nova/keys
%dir %{_sharedstatedir}/nova/networks
%dir %{_sharedstatedir}/nova/tmp

%dir %{_sharedstatedir}/nova/CA/
%dir %{_sharedstatedir}/nova/CA/certs
%dir %{_sharedstatedir}/nova/CA/crl
%dir %{_sharedstatedir}/nova/CA/newcerts
%dir %{_sharedstatedir}/nova/CA/projects
%dir %{_sharedstatedir}/nova/CA/reqs
%{_sharedstatedir}/nova/CA/*.sh
%{_sharedstatedir}/nova/CA/openssl.cnf.tmpl
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/cacert.pem
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/crl.pem
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/index.txt
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/openssl.cnf
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/serial
%dir %attr(0750, -, -) %{_sharedstatedir}/nova/CA/private
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) %{_sharedstatedir}/nova/CA/private/cakey.pem

%files -n python-nova
%defattr(-,root,root,-)
%doc LICENSE
%{python_sitelib}/nova
%{python_sitelib}/nova-%{version}-*.egg-info

%if 0%{?with_doc}
%files doc
%doc LICENSE doc/build/html
%endif

%changelog
* Mon Mar 12 2012 Marco Sinhoreli <marco.sinhoreli@corp.globo.com> - 2012.1-0.1.e4
- First release migrate from fedora-16 packages
