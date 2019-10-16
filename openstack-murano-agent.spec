# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global pypi_name murano-agent

Name:             openstack-murano-agent
Version:          4.0.0
Release:          1%{?dist}
Summary:          VM-side guest agent that accepts commands from Murano engine and executes them.
License:          ASL 2.0
URL:              http://git.openstack.org/cgit/openstack/%{pypi_name}
Source0:          https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
#

Source1:          openstack-murano-agent.service
Source2:          openstack-murano-agent.logrotate
BuildArch:        noarch

BuildRequires:    git
BuildRequires:    python%{pyver}-devel
BuildRequires:    python%{pyver}-pbr
BuildRequires:    python%{pyver}-setuptools
BuildRequires:    python%{pyver}-sphinx
BuildRequires:    python%{pyver}-oslo-config
BuildRequires:    python%{pyver}-oslo-log
BuildRequires:    python%{pyver}-oslo-service
BuildRequires:    python%{pyver}-oslo-utils
# test requirements
BuildRequires:    python%{pyver}-kombu
BuildRequires:    python%{pyver}-hacking
BuildRequires:    python%{pyver}-unittest2
BuildRequires:    python%{pyver}-mock
BuildRequires:    python%{pyver}-testtools
BuildRequires:    python%{pyver}-stestr
# doc build requirements
BuildRequires:    python%{pyver}-openstackdocstheme
BuildRequires:    python%{pyver}-sphinx
BuildRequires:    python%{pyver}-reno
BuildRequires:    systemd-units
BuildRequires:    openstack-macros

# Handle python2 exception
%if %{pyver} == 2
BuildRequires:    python-anyjson
BuildRequires:    GitPython
BuildRequires:    python-semantic_version
%else
BuildRequires:    python%{pyver}-anyjson
BuildRequires:    python%{pyver}-GitPython
BuildRequires:    python%{pyver}-semantic_version
%endif

Requires:         python%{pyver}-pbr >= 3.1.1
Requires:         python%{pyver}-six >= 1.11.0
Requires:         python%{pyver}-oslo-config >= 2:5.2.0
Requires:         python%{pyver}-oslo-log >= 3.37.0
Requires:         python%{pyver}-oslo-service >= 1.30.0
Requires:         python%{pyver}-oslo-utils >= 3.36.0
Requires:         python%{pyver}-requests >= 2.18.4
Requires:         python%{pyver}-eventlet >= 0.20.0
Requires:         python%{pyver}-kombu >= 1:4.1.0
Requires:         python%{pyver}-cryptography >= 2.1.4

# Handle python2 exception
%if %{pyver} == 2
Requires:         python-anyjson >= 0.3.3
Requires:         PyYAML >= 3.10
Requires:         GitPython >= 1.0.1
Requires:         python-semantic_version
%else
Requires:         python%{pyver}-anyjson >= 0.3.3
Requires:         python%{pyver}-PyYAML >= 3.10
Requires:         python%{pyver}-GitPython >= 1.0.1
Requires:         python%{pyver}-semantic_version
%endif

%{?systemd_requires}

%description
Murano Agent is the VM-side guest agent that accepts commands from Murano
engine and executes them

%prep
%autosetup -S git -n %{pypi_name}-%{upstream_version}

# Let RPM handle the dependencies
%py_req_cleanup

%build
%{pyver_build}

# Generate configuration files
PYTHONPATH=. oslo-config-generator-%{pyver} --config-file etc/oslo-config-generator/muranoagent.conf

# generate html docs
export OSLO_PACKAGE_VERSION=%{upstream_version}
sphinx-build-%{pyver} -W -b html doc/source doc/build/html

# remove the sphinx-build-%{pyver} leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}


%install
%{pyver_install}

# Install conf file
install -p -D -m 644 etc/muranoagent/muranoagent.conf.sample %{buildroot}%{_sysconfdir}/murano-agent/muranoagent.conf

# Install initscript for services
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/openstack-murano-agent.service

# Install logrotate
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/murano-agent

# Install log directory
install -d -m 755 %{buildroot}%{_localstatedir}/log/murano-agent

#install working directory for daemon
install -d -m 755 %{buildroot}%{_sharedstatedir}/murano-agent

%check
%{pyver_bin} setup.py test

%post
%systemd_post openstack-murano-agent

%preun
%systemd_preun openstack-murano-agent

%postun
%systemd_postun_with_restart openstack-murano-agent



%files
%license LICENSE
%doc README.rst
%doc doc/build/html
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/logrotate.d/murano-agent
%config(noreplace) %{_sysconfdir}/murano-agent/muranoagent.conf
%{_bindir}/muranoagent
%{_unitdir}/openstack-murano-agent.service
%dir %{_localstatedir}/log/murano-agent
%dir %{_sharedstatedir}/murano-agent
%{pyver_sitelib}/muranoagent
%{pyver_sitelib}/murano_agent-*.egg-info


%changelog
* Wed Oct 16 2019 RDO <dev@lists.rdoproject.org> 4.0.0-1
- Update to 4.0.0

* Mon Sep 30 2019 RDO <dev@lists.rdoproject.org> 4.0.0-0.1.0rc1
- Update to 4.0.0.0rc1

