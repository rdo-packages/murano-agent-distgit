%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global pypi_name murano-agent

Name:             openstack-murano-agent
Version:          XXX
Release:          XXX
Summary:          VM-side guest agent that accepts commands from Murano engine and executes them.
License:          ASL 2.0
URL:              http://git.openstack.org/cgit/openstack/%{pypi_name}
Source0:          https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:          openstack-murano-agent.service
Source2:          openstack-murano-agent.logrotate
BuildArch:        noarch

BuildRequires:    git
BuildRequires:    python2-devel
BuildRequires:    python2-pbr
BuildRequires:    python2-setuptools
BuildRequires:    python2-sphinx
BuildRequires:    python2-oslo-config
BuildRequires:    python2-oslo-log
BuildRequires:    python2-oslo-service
BuildRequires:    python2-oslo-utils
# test requirements
BuildRequires:    python2-kombu
BuildRequires:    python-anyjson
BuildRequires:    python-semantic-version
BuildRequires:    GitPython
BuildRequires:    python2-hacking
BuildRequires:    python-unittest2
BuildRequires:    python2-mock
BuildRequires:    python2-testtools
BuildRequires:    python2-stestr
# doc build requirements
BuildRequires:    python2-openstackdocstheme
BuildRequires:    python2-sphinx
BuildRequires:    python2-reno
BuildRequires:    systemd-units
BuildRequires:    openstack-macros

Requires:         python2-pbr >= 2.0.0
Requires:         python2-six >= 1.10.0
Requires:         python2-oslo-config >= 2:5.1.0
Requires:         python2-oslo-log >= 3.36.0
Requires:         python2-oslo-service >= 1.24.0
Requires:         python2-oslo-utils >= 3.33.0
Requires:         python2-requests >= 2.14.2
Requires:         python-anyjson >= 0.3.3
Requires:         python2-eventlet >= 0.18.2
Requires:         GitPython >= 1.0.1
Requires:         PyYAML >= 3.10
Requires:         python-semantic-version
Requires:         python2-kombu >= 1:4.0.0
Requires:         python2-cryptography >= 1.7.2
%{?systemd_requires}

%description
Murano Agent is the VM-side guest agent that accepts commands from Murano
engine and executes them

%prep
%autosetup -S git -n %{pypi_name}-%{upstream_version}

# Let RPM handle the dependencies
%py_req_cleanup

%build
%py2_build

# Generate configuration files
PYTHONPATH=. oslo-config-generator --config-file etc/oslo-config-generator/muranoagent.conf

# generate html docs
export OSLO_PACKAGE_VERSION=%{upstream_version}
%{__python2} setup.py build_sphinx -b html

# remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}


%install
%py2_install

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
%{__python2} setup.py test

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
%{python2_sitelib}/muranoagent
%{python2_sitelib}/murano_agent-*.egg-info


%changelog
