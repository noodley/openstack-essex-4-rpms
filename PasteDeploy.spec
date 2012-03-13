%define name PasteDeploy
%define version 1.5.0
%define unmangled_version 1.5.0
%define unmangled_version 1.5.0
%define release 1

Summary: Load, configure, and compose WSGI applications and servers
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Alex Gronholm <alex.gronholm@nextday.fi>
Url: http://pythonpaste.org/deploy/

%description
This tool provides code to load WSGI applications and servers from
URIs; these URIs can refer to Python Eggs for INI-style configuration
files.  `Paste Script <http://pythonpaste.org/script>`_ provides
commands to serve applications based on this configuration file.

The latest version is available in a `Mercurial repository
<http://bitbucket.org/ianb/pastedeploy>`_ (or a `tarball
<http://bitbucket.org/ianb/pastedeploy/get/tip.gz#egg=PasteDeploy-dev>`_).

For the latest changes see the `news file
<http://pythonpaste.org/deploy/news.html>`_.


%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
