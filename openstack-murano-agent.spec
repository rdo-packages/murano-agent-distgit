%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
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
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif
BuildArch:        noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif

BuildRequires:    git-core
BuildRequires:    python3-devel
BuildRequires:    python3-pbr
BuildRequires:    python3-setuptools
BuildRequires:    python3-sphinx
BuildRequires:    python3-oslo-config
BuildRequires:    python3-oslo-log
BuildRequires:    python3-oslo-service
BuildRequires:    python3-oslo-utils
# test requirements
BuildRequires:    python3-kombu
BuildRequires:    python3-hacking
BuildRequires:    python3-mock
BuildRequires:    python3-testtools
BuildRequires:    python3-stestr
# doc build requirements
BuildRequires:    python3-openstackdocstheme
BuildRequires:    python3-sphinx
BuildRequires:    python3-reno
BuildRequires:    systemd-units
BuildRequires:    openstack-macros

BuildRequires:    python3-GitPython
BuildRequires:    python3-semantic_version

Requires:         python3-pbr >= 5.5.1
Requires:         python3-oslo-config >= 2:6.8.0
Requires:         python3-oslo-log >= 4.4.0
Requires:         python3-oslo-service >= 2.5.0
Requires:         python3-oslo-utils >= 4.8.0
Requires:         python3-requests >= 2.25.1
Requires:         python3-eventlet >= 0.30.1
Requires:         python3-kombu >= 1:4.6.1
Requires:         python3-cryptography >= 2.7

Requires:         python3-yaml >= 5.1
Requires:         python3-GitPython >= 3.0.5
Requires:         python3-semantic_version >= 2.6.0

%{?systemd_requires}

%description
Murano Agent is the VM-side guest agent that accepts commands from Murano
engine and executes them

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -S git -n %{pypi_name}-%{upstream_version}

# Let RPM handle the dependencies
%py_req_cleanup

%build
%{py3_build}

# Generate configuration files
PYTHONPATH=. oslo-config-generator --config-file etc/oslo-config-generator/muranoagent.conf

# generate html docs
export OSLO_PACKAGE_VERSION=%{upstream_version}
sphinx-build -W -b html doc/source doc/build/html

# remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}


%install
%{py3_install}

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
%{__python3} setup.py test

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
%{python3_sitelib}/muranoagent
%{python3_sitelib}/murano_agent-*.egg-info


%changelog
