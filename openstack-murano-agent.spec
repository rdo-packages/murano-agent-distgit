%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global pypi_name murano-agent

Name:             openstack-murano-agent
Version:          6.0.0
Release:          2%{?dist}
Summary:          VM-side guest agent that accepts commands from Murano engine and executes them.
License:          ASL 2.0
URL:              http://git.openstack.org/cgit/openstack/%{pypi_name}
Source0:          https://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
#

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

BuildRequires:    git
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
BuildRequires:    python3-unittest2
BuildRequires:    python3-mock
BuildRequires:    python3-testtools
BuildRequires:    python3-stestr
# doc build requirements
BuildRequires:    python3-openstackdocstheme
BuildRequires:    python3-sphinx
BuildRequires:    python3-reno
BuildRequires:    systemd-units
BuildRequires:    openstack-macros

BuildRequires:    python3-anyjson
BuildRequires:    python3-GitPython
BuildRequires:    python3-semantic_version

Requires:         python3-pbr >= 3.1.1
Requires:         python3-oslo-config >= 2:5.2.0
Requires:         python3-oslo-log >= 3.37.0
Requires:         python3-oslo-service >= 1.30.0
Requires:         python3-oslo-utils >= 3.36.0
Requires:         python3-requests >= 2.18.4
Requires:         python3-eventlet >= 0.20.0
Requires:         python3-kombu >= 1:4.3.0
Requires:         python3-cryptography >= 2.1.4

Requires:         python3-anyjson >= 0.3.3
Requires:         python3-PyYAML >= 3.10
Requires:         python3-GitPython >= 1.0.1
Requires:         python3-semantic_version

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
* Tue Oct 20 2020 Joel Capitao <jcapitao@redhat.com> 6.0.0-2
- Enable sources tarball validation using GPG signature.

* Wed Oct 14 2020 RDO <dev@lists.rdoproject.org> 6.0.0-1
- Update to 6.0.0

* Thu Sep 24 2020 RDO <dev@lists.rdoproject.org> 6.0.0-0.1.0rc1
- Update to 6.0.0.0rc1

