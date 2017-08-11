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
BuildRequires:    python-devel
BuildRequires:    python-pbr
BuildRequires:    python-setuptools
BuildRequires:    python-sphinx
BuildRequires:    python-oslo-config
BuildRequires:    python-oslo-log
BuildRequires:    python-oslo-service
BuildRequires:    python-oslo-utils
# test requirements
BuildRequires:    python-kombu
BuildRequires:    python-anyjson
BuildRequires:    python-semantic-version
BuildRequires:    GitPython
BuildRequires:    python-hacking
BuildRequires:    python-unittest2
BuildRequires:    python-mock
BuildRequires:    python-testtools
BuildRequires:    python-testrepository
# doc build requirements
BuildRequires:    python-openstackdocstheme
BuildRequires:    python-sphinx
BuildRequires:    python-reno
BuildRequires:    systemd-units

Requires:         python-pbr >= 2.0.0
Requires:         python-six >= 1.9.0
Requires:         python-oslo-config >= 2:4.0.0
Requires:         python-oslo-log >= 3.22.0
Requires:         python-oslo-service >= 1.10.0
Requires:         python-oslo-utils >= 3.20.0
Requires:         python-requests >= 2.10.0
Requires:         python-anyjson >= 0.3.3
Requires:         python-eventlet >= 0.18.2
Requires:         GitPython >= 1.0.1
Requires:         PyYAML >= 3.10
Requires:         python-semantic-version
Requires:         python-kombu >= 1:4.0.0
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd


%description
Murano Agent is the VM-side guest agent that accepts commands from Murano
engine and executes them

%prep
%autosetup -S git -n %{pypi_name}-%{upstream_version}

# Let RPM handle the dependencies
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

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
%{__python2} setup.py testr

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
