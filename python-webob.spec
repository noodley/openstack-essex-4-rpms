%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-webob
Summary:        WSGI request and response object
Version:        1.1.1
Release:        1%{?dist}
License:        MIT
Group:          System Environment/Libraries
URL:            http://pythonpaste.org/webob/
Source0:        Web0b-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-setuptools-devel
BuildRequires:  python-nose
BuildRequires:  python-dtopt
BuildRequires:  python-tempita
BuildRequires:  python-wsgiproxy

%description
WebOb provides wrappers around the WSGI request environment, and an object to 
help create WSGI responses. The objects map much of the specified behavior of 
HTTP, including header parsing and accessors for other standard parts of the 
environment.

%prep
%setup -q -n WebOb-%{version}
# Disable the tests that require python-webtest
# (which depends on python-webob to begin with)
%{__rm} -f tests/test_request.py
# Disable conftest, which assumes that WebOb is already installed
%{__rm} -f tests/conftest.py
# Disable performance_test, which requires repoze.profile, which isn't
# in Fedora.
%{__rm} -f tests/performance_test.py


%build
%{__python} setup.py build


%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}


%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc docs/*
%{python_sitelib}/webob/
%{python_sitelib}/WebOb*.egg-info/

%changelog
* Mon Mar 12 2012 Marco Sinhoreli <marco.sinhoreli@corp.globo.com> 1.1.1-1
- Initial release for CentOS

