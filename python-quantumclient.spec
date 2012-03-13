#
# This is 2012.1 essex-4 milestone
#
%global release_name essex
%global release_letter e
%global milestone 4

Name:       python-quantumclient
Version:    2012.1
Release:    0.3.%{release_letter}%{milestone}%{?dist}
Summary:    Python API and CLI for OpenStack Quantum

Group:      Development/Languages
License:    ASL 2.0
URL:        https://github.com/openstack/python-quantumclient
BuildArch:  noarch

Source0:    python-quantumclient-2012.1~e4~20120229.r16.tar.gz

# Previously python-quantum owned /usr/lib/python/site-package/quantum
# Newer versions will require this package. Users will have to upgrade
# both simultaneously.
Conflicts:  python-quantum <= 2011.3

Requires:   python-gflags
Requires:   python-paste-deploy

BuildRequires: python2-devel
BuildRequires: python-setuptools

%description
Client library and command line utility for interacting with Openstack
Quantum's API.

%prep
%setup -q

# https://bugs.launchpad.net/quantum/+bug/944363
rm quantum/vcsversion.py

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}


%files
%doc README
%{_bindir}/quantum
%{python_sitelib}/quantum
%{python_sitelib}/*.egg-info


%changelog
* Tue Mar  13 2012 Marco Sinhoreli <marco.sinhoreli@corp.globo.com> - 2012.1-0.3.e4
- Update package to essex-4 rc16

* Thu Mar  1 2012 Robert Kukura <rkukura@redhat.com> - 2012.1-0.2.e4
- Update to essex milestone 4

* Thu Jan 26 2012 Cole Robinson <crobinso@redhat.com> - 2012.1-0.1.e3
- Initial package
