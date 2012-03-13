%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name:           python-paste-deploy
Version:        1.5.0
Release:        1%{?dist}
Summary:        Load, configure, and compose WSGI applications and servers
Group:          System Environment/Libraries
License:        MIT
URL:            http://pythonpaste.org/deploy
Source0:        http://cheeseshop.python.org/packages/source/P/PasteDeploy/PasteDeploy-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires: python-devel
%if 0%{?fedora} >= 8 || 0%{?rhel} >= 6
BuildRequires: python-setuptools-devel
%else
BuildRequires: python-setuptools
%endif
Requires:       python-paste

%description
This tool provides code to load WSGI applications and servers from
URIs; these URIs can refer to Python Eggs for INI-style configuration
files.  PasteScript provides commands to serve applications based on
this configuration file.

%prep
%setup -q -n PasteDeploy-%{version}


%build
%{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install --single-version-externally-managed \
                             --skip-build -O1 --root=%{buildroot}

echo '%defattr (0644,root,root,0755)' > pyfiles
find %{buildroot}%{python_sitelib}/paste/deploy -type d | \
        sed 's:%{buildroot}\(.*\):%dir \1:' >> pyfiles
find %{buildroot}%{python_sitelib}/paste/deploy -not -type d | \
        sed 's:%{buildroot}\(.*\):\1:' >> pyfiles

%clean
rm -rf %{buildroot}


%files -f pyfiles
%defattr(-,root,root,-)
%doc docs/*
%{python_sitelib}/PasteDeploy-%{version}-py%{pyver}*



%changelog
* Mon Mar 12 2012 Marco Sinhoreli <marco.sinhoreli@corp.globo.com> - 1.5.0-1
- First Release
