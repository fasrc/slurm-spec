Name:		slurm
Version:	24.11.4
%define rel	1
%if %{defined patch} && %{undefined extraver}
%define extraver .patched
%endif
Release:	%{rel}%{?extraver}fasrc01%{?dist}
Summary:	Slurm Workload Manager

Group:		System Environment/Base
License:	GPLv2+
URL:		https://slurm.schedmd.com/

# when the rel number is one, the directory name does not include it
%if "%{rel}" == "1"
%global slurm_source_dir %{name}-%{version}
%else
%global slurm_source_dir %{name}-%{version}-%{rel}
%endif

Source:		%{slurm_source_dir}.tar.bz2
%{lua: local patchnum=0
  for pfile in string.gmatch(rpm.expand("%{?patch}"), "%S+") do
    print('Patch'..patchnum..':\t'..pfile..'\n')
    patchnum=patchnum+1
  end
}

# build options		.rpmmacros options	change to default action
# ====================  ====================	========================
# --prefix		%_prefix path		install path for commands, libraries, etc.
# --with cray_shasta	%_with_cray_shasta 1	build for a Cray Shasta system
# --with slurmrestd	%_with_slurmrestd 1	build slurmrestd
# --with yaml		%_with_yaml 1		build with yaml serializer
# --without debug	%_without_debug 1	don't compile with debugging symbols
# --with hdf5		%_with_hdf5 path	require hdf5 support
# --with hwloc		%_with_hwloc 1		require hwloc support
# --with libcurl	%_with_libcurl 1	require libcurl support
# --with lua		%_with_lua path		build Slurm lua bindings
# --without munge	%_without_munge 1	disable support for munge
# --with numa		%_with_numa 1		require NUMA support
# --without pam		%_without_pam 1		don't require pam-devel RPM to be installed
# --without x11		%_without_x11 1		disable internal X11 support
# --with ucx		%_with_ucx path		require ucx support
# --with pmix		%_with_pmix path	build with pmix support
# --with nvml		%_with_nvml path	require nvml support
# --with jwt		%_with_jwt 1		require jwt support
# --with freeipmi	%_with_freeipmi 1	require freeipmi support
# --with selinux	%_with_selinux 1	build with selinux support
#

%define _with_slurmrestd 1
%define _with_pmix --with-pmix

#  Options that are off by default (enable with --with <opt>)
%bcond_with cray_shasta
%bcond_with slurmrestd
%bcond_with multiple_slurmd
%bcond_with pmix
%bcond_with ucx

# These options are only here to force there to be these on the build.
# If they are not set they will still be compiled if the packages exist.
%bcond_with hwloc
%bcond_with hdf5
%bcond_with libcurl
%bcond_with lua
%bcond_with numa
%bcond_with nvml
%bcond_with jwt
%bcond_with yaml
%bcond_with freeipmi

# Use debug by default on all systems
%bcond_without debug

# Options enabled by default
%bcond_without munge
%bcond_without pam
%bcond_without x11

# Disable hardened builds. -z,now or -z,relro breaks the plugin stack
%undefine _hardened_build
%global _hardened_cflags "-Wl,-z,lazy"
%global _hardened_ldflags "-Wl,-z,lazy"

# Disable Link Time Optimization (LTO)
%define _lto_cflags %{nil}

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  gcc
BuildRequires:  make
%if %{defined suse_version}
BuildRequires: pkg-config
%else
%if (0%{?rhel} != 7)
BuildRequires:  pkgconf
%else
BuildRequires:  pkgconfig
%endif
%endif

%if %{with munge}
Requires: munge
BuildRequires: munge-devel munge-libs
%endif

Requires: bash-completion

%{?systemd_requires}
BuildRequires: systemd
BuildRequires: python3
BuildRequires: readline-devel
Obsoletes: slurm-lua <= %{version}
Obsoletes: slurm-munge <= %{version}
Obsoletes: slurm-plugins <= %{version}

# fake systemd support when building rpms on other platforms
%{!?_unitdir: %global _unitdir /lib/systemd/systemd}

%define use_mysql_devel %(perl -e '`rpm -q mysql-devel`; print !$?;')
# Default for OpenSUSE/SLES builds
%define use_libmariadb_devel %(perl -e '`rpm -q libmariadb-devel`; print !$?;')
# Package name from the official MariaDB version
%define use_MariaDB_devel %(perl -e '`rpm -q MariaDB-devel`; print !$?;')
# Oracle mysql community
%define use_mysql_community %(perl -e '`rpm -q mysql-community-devel`; print !$?;')
# Oracle mysql commercial
%define use_mysql_commercial %(perl -e '`rpm -q mysql-commercial-devel`; print !$?;')

%if 0%{?use_mysql_devel}
BuildRequires: mysql-devel >= 5.0.0
%else
%if 0%{?use_mysql_community}
BuildRequires: mysql-community-devel >= 5.0.0
%else
%if 0%{?use_mysql_commercial}
BuildRequires: mysql-commercial-devel >= 5.0.0
%else
%if 0%{?use_libmariadb_devel}
# OpenSUSE/SLES has a different versioning scheme, so skip the version check
BuildRequires: libmariadb-devel
%else
%if 0%{?use_MariaDB_devel}
BuildRequires: MariaDB-devel >= 5.0.0
%else
BuildRequires: mariadb-devel >= 5.0.0
%endif
%endif
%endif
%endif
%endif

BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: libcurl-devel
BuildRequires: numactl-devel
BuildRequires: json-c-devel
BuildRequires: infiniband-diags-devel
BuildRequires: rdma-core-devel
BuildRequires: lz4-devel
BuildRequires: man2html
BuildRequires: http-parser-devel
BuildRequires: libyaml-devel
BuildRequires: hdf5-devel
BuildRequires: freeipmi-devel
BuildRequires: rrdtool-devel
BuildRequires: hwloc-devel
BuildRequires: lua-devel
BuildRequires: mysql-devel
BuildRequires: gtk2-devel
BuildRequires: glib2-devel
BuildRequires: dbus-devel
BuildRequires: librdkafka-devel
BuildRequires: s2n-tls-devel
BuildRequires: libjwt-devel
BuildRequires: cuda-nvml-devel-12-4

%if %{defined suse_version}
BuildRequires: perl
%else
BuildRequires: perl-devel
%endif

%if %{with lua}
BuildRequires: pkgconfig(lua) >= 5.1.0
%endif

%if %{with hwloc} && "%{_with_hwloc}" == "--with-hwloc"
BuildRequires: hwloc-devel
%endif

%if %{with numa}
%if %{defined suse_version}
BuildRequires: libnuma-devel
%else
BuildRequires: numactl-devel
%endif
%endif

%if %{with pmix} && "%{_with_pmix}" == "--with-pmix"
BuildRequires: pmix
%global pmix_version %(rpm -q pmix --qf "%{RPMTAG_VERSION}")
%endif

%if %{with ucx} && "%{_with_ucx}" == "--with-ucx"
BuildRequires: ucx-devel
%global ucx_version %(rpm -q ucx-devel --qf "%{RPMTAG_VERSION}")
%endif

%if %{with libcurl}
%if %{defined suse_version}
Requires: libcurl
%else
Requires: libcurl4
%endif
BuildRequires: libcurl-devel
%endif

%if %{with jwt}
BuildRequires: libjwt-devel >= 1.10.0
Requires: libjwt >= 1.10.0
%endif

%if %{with yaml}
Requires: libyaml >= 0.2.5
BuildRequires: libyaml-devel >= 0.2.5
%endif

%if %{with freeipmi}
Requires: freeipmi
BuildRequires: freeipmi-devel
%endif

%if %{with selinux}
Requires: libselinux
BuildRequires: libselinux-devel
%endif

#  Allow override of sysconfdir via _slurm_sysconfdir.
#  Note 'global' instead of 'define' needed here to work around apparent
#   bug in rpm macro scoping (or something...)
%{!?_slurm_sysconfdir: %global _slurm_sysconfdir /etc/slurm}
%define _sysconfdir %_slurm_sysconfdir

#  Allow override of datadir via _slurm_datadir.
%{!?_slurm_datadir: %global _slurm_datadir %{_prefix}/share}
%define _datadir %{_slurm_datadir}

#  Allow override of mandir via _slurm_mandir.
%{!?_slurm_mandir: %global _slurm_mandir %{_datadir}/man}
%define _mandir %{_slurm_mandir}

#
# Never allow rpm to strip binaries as this will break
#  parallel debugging capability
# Note that brp-compress does not compress man pages installed
#  into non-standard locations (e.g. /usr/local)
#
%define __os_install_post /usr/lib/rpm/brp-compress
%define debug_package %{nil}

#
# Should unpackaged files in a build root terminate a build?
# Uncomment if needed again.
#%define _unpackaged_files_terminate_build      0

# Slurm may intentionally include empty manifest files, which will
# cause errors with rpm 4.13 and on. Turn that check off.
%define _empty_manifest_terminate_build 0

# First we remove $prefix/local and then just prefix to make
# sure we get the correct installdir
%define _perlarch %(perl -e 'use Config; $T=$Config{installsitearch}; $P=$Config{installprefix}; $P1="$P/local"; $T =~ s/$P1//; $T =~ s/$P//; print $T;')

%define _perlman3 %(perl -e 'use Config; $T=$Config{installsiteman3dir}; $P=$Config{siteprefix}; $P1="$P/local"; $T =~ s/$P1//; $T =~ s/$P//; print $T;')

%define _perlarchlib %(perl -e 'use Config; $T=$Config{installarchlib}; $P=$Config{installprefix}; $P1="$P/local"; $T =~ s/$P1//; $T =~ s/$P//; print $T;')

%define _perldir %{_prefix}%{_perlarch}
%define _perlman3dir %{_prefix}%{_perlman3}
%define _perlarchlibdir %{_prefix}%{_perlarchlib}

%description
Slurm is an open source, fault-tolerant, and highly scalable
cluster management and job scheduling system for Linux clusters.
Components include machine status, partition management,
job management, scheduling and accounting modules

%package perlapi
Summary: Perl API to Slurm
Group: Development/System
Requires: %{name}%{?_isa} = %{version}-%{release}
%description perlapi
Perl API package for Slurm.  This package includes the perl API to provide a
helpful interface to Slurm through Perl

%package devel
Summary: Development package for Slurm
Group: Development/System
Requires: %{name}%{?_isa} = %{version}-%{release}
%description devel
Development package for Slurm.  This package includes the header files
and static libraries for the Slurm API

%package example-configs
Summary: Example config files for Slurm
Group: Development/System
%description example-configs
Example configuration files for Slurm.

%package sackd
Summary: Slurm authentication daemon
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
%description sackd
Slurm authentication daemon. Used on login nodes that are not running slurmd
daemons to allow authentication to the cluster.

%package slurmctld
Summary: Slurm controller daemon
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
%if %{with pmix} && "%{_with_pmix}" == "--with-pmix"
Requires: pmix = %{pmix_version}
%endif
%if %{with ucx} && "%{_with_ucx}" == "--with-ucx"
Requires: ucx = %{ucx_version}
%endif
%description slurmctld
Slurm controller daemon. Used to manage the job queue, schedule jobs,
and dispatch RPC messages to the slurmd processon the compute nodes
to launch jobs.

%package slurmd
Summary: Slurm compute node daemon
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
%if %{with pmix} && "%{_with_pmix}" == "--with-pmix"
Requires: pmix = %{pmix_version}
%endif
%if %{with ucx} && "%{_with_ucx}" == "--with-ucx"
Requires: ucx = %{ucx_version}
%endif
%description slurmd
Slurm compute node daemon. Used to launch jobs on compute nodes

%package slurmdbd
Summary: Slurm database daemon
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: slurm-sql <= %{version}
%description slurmdbd
Slurm database daemon. Used to accept and process database RPCs and upload
database changes to slurmctld daemons on each cluster

%package libpmi
Summary: Slurm\'s implementation of the pmi libraries
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
Conflicts: pmix-libpmi
%description libpmi
Slurm\'s version of libpmi. For systems using Slurm, this version
is preferred over the compatibility libraries shipped by the PMIx project.

%package torque
Summary: Torque/PBS wrappers for transition from Torque/PBS to Slurm
Group: Development/System
Requires: slurm-perlapi
%description torque
Torque wrapper scripts used for helping migrate from Torque/PBS to Slurm

%package openlava
Summary: openlava/LSF wrappers for transition from OpenLava/LSF to Slurm
Group: Development/System
Requires: slurm-perlapi
%description openlava
OpenLava wrapper scripts used for helping migrate from OpenLava/LSF to Slurm

%package contribs
Summary: Perl tool to print Slurm job state information
Group: Development/System
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: slurm-sjobexit <= %{version}
Obsoletes: slurm-sjstat <= %{version}
Obsoletes: slurm-seff <= %{version}
%description contribs
seff is a mail program used directly by the Slurm daemons. On completion of a
job, wait for it's accounting information to be available and include that
information in the email body.
sjobexit is a slurm job exit code management tool. It enables users to alter
job exit code information for completed jobs
sjstat is a Perl tool to print Slurm job state information. The output is designed
to give information on the resource usage and availablilty, as well as information
about jobs that are currently active on the machine. This output is built
using the Slurm utilities, sinfo, squeue and scontrol, the man pages for these
utilities will provide more information and greater depth of understanding.

%if %{with pam}
%package pam_slurm
Summary: PAM module for restricting access to compute nodes via Slurm
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
BuildRequires: pam-devel
Obsoletes: pam_slurm <= %{version}
%description pam_slurm
This module restricts access to compute nodes in a cluster where Slurm is in
use.  Access is granted to root, any user with an Slurm-launched job currently
running on the node, or any user who has allocated resources on the node
according to the Slurm
%endif

%if %{with slurmrestd}
%package slurmrestd
Summary: Slurm REST API translator
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
BuildRequires: http-parser-devel
%if %{defined suse_version}
BuildRequires: libjson-c-devel
%else
BuildRequires: json-c-devel
%endif
%description slurmrestd
Provides a REST interface to Slurm.
%endif

#############################################################################

%prep
# when the rel number is one, the tarball filename does not include it
%setup -n %{slurm_source_dir}
%global _default_patch_fuzz 2
%autopatch -p1

%build

export CFLAGS="$CFLAGS -L/usr/local/cuda-12.4/targets/x86_64-linux/lib/stubs/ -I/usr/local/cuda-12.4/targets/x86_64-linux/include/"

%configure \
	--with-systemdsystemunitdir=%{_unitdir} \
	--enable-pkgconfig \
	%{?_without_debug:--disable-debug} \
	%{?_with_pam_dir} \
	%{?_with_mysql_config} \
	%{?_with_multiple_slurmd:--enable-multiple-slurmd} \
	%{?_with_selinux:--enable-selinux} \
	%{?_with_pmix} \
	%{?_with_freeipmi} \
	%{?_with_hdf5} \
	%{?_with_hwloc} \
	%{?_with_shared_libslurm} \
	%{!?_with_slurmrestd:--disable-slurmrestd} \
	%{?_without_x11:--disable-x11} \
	%{?_with_libcurl} \
	%{?_with_ucx} \
	%{?_with_jwt} \
	%{?_with_yaml} \
	%{?_with_nvml} \
	%{?_with_freeipmi} \
	%{!?with_munge:--without-munge} \
	%{?_with_cflags}

make %{?_smp_mflags}

%install

# Ignore redundant standard rpaths and insecure relative rpaths,
# for RHEL based distros which use "check-rpaths" tool.
export QA_RPATHS=0x5

# Strip out some dependencies

cat > find-requires.sh <<'EOF'
exec %{__find_requires} "$@" | grep -E -v '^libpmix.so|libevent|libnvidia-ml'
EOF
chmod +x find-requires.sh
%global _use_internal_dependency_generator 0
%global __find_requires %{_builddir}/%{buildsubdir}/find-requires.sh

rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
make install-contrib DESTDIR=%{buildroot}

# Do not package Slurm's version of libpmi on Cray systems in the usual location.
# Cray's version of libpmi should be used. Move it elsewhere if the site still
# wants to use it with other MPI stacks.
%if %{with cray_shasta}
   mkdir %{buildroot}/%{_libdir}/slurmpmi
   mv %{buildroot}/%{_libdir}/libpmi* %{buildroot}/%{_libdir}/slurmpmi
%endif

install -D -m644 etc/cgroup.conf.example %{buildroot}/%{_sysconfdir}/cgroup.conf.example
install -D -m644 etc/prolog.example %{buildroot}/%{_sysconfdir}/prolog.example
install -D -m644 etc/job_submit.lua.example %{buildroot}/%{_sysconfdir}/job_submit.lua.example
install -D -m644 etc/slurm.conf.example %{buildroot}/%{_sysconfdir}/slurm.conf.example
install -D -m600 etc/slurmdbd.conf.example %{buildroot}/%{_sysconfdir}/slurmdbd.conf.example
install -D -m644 etc/cli_filter.lua.example %{buildroot}/%{_sysconfdir}/cli_filter.lua.example
install -D -m755 contribs/sjstat %{buildroot}/%{_bindir}/sjstat

# Delete unpackaged files:
find %{buildroot} -name '*.a' -exec rm {} \;
find %{buildroot} -name '*.la' -exec rm {} \;
rm -f %{buildroot}/%{_libdir}/slurm/job_submit_defaults.so
rm -f %{buildroot}/%{_libdir}/slurm/job_submit_logging.so
rm -f %{buildroot}/%{_libdir}/slurm/job_submit_partition.so
rm -f %{buildroot}/%{_libdir}/slurm/auth_none.so
rm -f %{buildroot}/%{_libdir}/slurm/cred_none.so
rm -f %{buildroot}/%{_sbindir}/sfree
rm -f %{buildroot}/%{_sbindir}/slurm_epilog
rm -f %{buildroot}/%{_sbindir}/slurm_prolog
rm -f %{buildroot}/%{_sysconfdir}/init.d/slurm
rm -f %{buildroot}/%{_sysconfdir}/init.d/slurmdbd
rm -f %{buildroot}/%{_perldir}/auto/Slurm/.packlist
rm -f %{buildroot}/%{_perldir}/auto/Slurm/Slurm.bs
rm -f %{buildroot}/%{_perlarchlibdir}/perllocal.pod
rm -f %{buildroot}/%{_perldir}/perllocal.pod
rm -f %{buildroot}/%{_perldir}/auto/Slurmdb/.packlist
rm -f %{buildroot}/%{_perldir}/auto/Slurmdb/Slurmdb.bs
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sacct
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sacctmgr
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/salloc
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sattach
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sbatch
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sbcast
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/scancel
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/scontrol
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/scrontab
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sdiag
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sinfo
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/slurmrestd
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sprio
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/squeue
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sreport
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/srun
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sshare
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/sstat
rm -f %{buildroot}/%{_datadir}/bash-completion/completions/strigger

# Build man pages that are generated directly by the tools
rm -f %{buildroot}/%{_mandir}/man1/sjobexitmod.1
%{buildroot}/%{_bindir}/sjobexitmod --roff > %{buildroot}/%{_mandir}/man1/sjobexitmod.1
rm -f %{buildroot}/%{_mandir}/man1/sjstat.1
%{buildroot}/%{_bindir}/sjstat --roff > %{buildroot}/%{_mandir}/man1/sjstat.1

LIST=./pam.files
touch $LIST
%if %{?with_pam_dir}0
    test -f %{buildroot}/%{with_pam_dir}/pam_slurm.so	&&
	echo %{with_pam_dir}/pam_slurm.so	>>$LIST
    test -f %{buildroot}/%{with_pam_dir}/pam_slurm_adopt.so	&&
	echo %{with_pam_dir}/pam_slurm_adopt.so	>>$LIST
%else
    test -f %{buildroot}/lib/security/pam_slurm.so	&&
	echo /lib/security/pam_slurm.so		>>$LIST
    test -f %{buildroot}/lib32/security/pam_slurm.so	&&
	echo /lib32/security/pam_slurm.so	>>$LIST
    test -f %{buildroot}/lib64/security/pam_slurm.so	&&
	echo /lib64/security/pam_slurm.so	>>$LIST
    test -f %{buildroot}/lib/security/pam_slurm_adopt.so		&&
	echo /lib/security/pam_slurm_adopt.so		>>$LIST
    test -f %{buildroot}/lib32/security/pam_slurm_adopt.so		&&
	echo /lib32/security/pam_slurm_adopt.so		>>$LIST
    test -f %{buildroot}/lib64/security/pam_slurm_adopt.so		&&
	echo /lib64/security/pam_slurm_adopt.so		>>$LIST
%endif
#############################################################################

%clean
rm -rf %{buildroot}
#############################################################################

%files
%defattr(-,root,root,0755)
%{_datadir}/doc
%{_bindir}/s*
%exclude %{_bindir}/seff
%exclude %{_bindir}/sjobexitmod
%exclude %{_bindir}/sjstat
%exclude %{_bindir}/smail
%exclude %{_libdir}/libpmi*
%{_libdir}/*.so*
%{_libdir}/slurm/src/*
%{_libdir}/slurm/*.so
%exclude %{_libdir}/slurm/accounting_storage_mysql.so
%exclude %{_libdir}/slurm/job_submit_pbs.so
%exclude %{_libdir}/slurm/spank_pbs.so
%{_mandir}
%exclude %{_mandir}/man1/sjobexit*
%exclude %{_mandir}/man1/sjstat*
%dir %{_libdir}/slurm/src
%{_datadir}/bash-completion/completions/slurm_completion.sh
#############################################################################

%files example-configs
%defattr(-,root,root,0755)
%dir %{_sysconfdir}
%config %{_sysconfdir}/cgroup.conf.example
%config %{_sysconfdir}/job_submit.lua.example
%config %{_sysconfdir}/prolog.example
%config %{_sysconfdir}/slurm.conf.example
%config %{_sysconfdir}/slurmdbd.conf.example
%config %{_sysconfdir}/cli_filter.lua.example
#############################################################################

%files devel
%defattr(-,root,root)
%dir %attr(0755,root,root)
%dir %{_prefix}/include/slurm
%{_prefix}/include/slurm/*
%{_libdir}/pkgconfig/slurm.pc
#############################################################################

%files perlapi
%defattr(-,root,root)
%{_perldir}/Slurm.pm
%{_perldir}/Slurm/Bitstr.pm
%{_perldir}/Slurm/Constant.pm
%{_perldir}/Slurm/Hostlist.pm
%{_perldir}/auto/Slurm/Slurm.so
%{_perldir}/Slurmdb.pm
%{_perldir}/auto/Slurmdb/Slurmdb.so
%{_perldir}/auto/Slurmdb/autosplit.ix
%{_perlman3dir}/Slurm*

#############################################################################

%files sackd
%defattr(-,root,root)
%{_sbindir}/sackd
%{_unitdir}/sackd.service
#############################################################################

%files slurmctld
%defattr(-,root,root)
%{_sbindir}/slurmctld
%{_unitdir}/slurmctld.service
#############################################################################

%files slurmd
%defattr(-,root,root)
%{_sbindir}/slurmd
%{_sbindir}/slurmstepd
%{_unitdir}/slurmd.service
#############################################################################

%files slurmdbd
%defattr(-,root,root)
%{_sbindir}/slurmdbd
%{_libdir}/slurm/accounting_storage_mysql.so
%{_unitdir}/slurmdbd.service
#############################################################################

%files libpmi
%defattr(-,root,root)
%if %{with cray_shasta}
%{_libdir}/slurmpmi/*
%else
%{_libdir}/libpmi*
%endif
#############################################################################

%files torque
%defattr(-,root,root)
%{_bindir}/pbsnodes
%{_bindir}/qalter
%{_bindir}/qdel
%{_bindir}/qhold
%{_bindir}/qrerun
%{_bindir}/qrls
%{_bindir}/qstat
%{_bindir}/qsub
%{_bindir}/mpiexec
%{_bindir}/generate_pbs_nodefile
%{_libdir}/slurm/job_submit_pbs.so
%{_libdir}/slurm/spank_pbs.so
#############################################################################

%files openlava
%defattr(-,root,root)
%{_bindir}/bjobs
%{_bindir}/bkill
%{_bindir}/bsub
%{_bindir}/lsid

#############################################################################

%files contribs
%defattr(-,root,root)
%{_bindir}/seff
%{_bindir}/sjobexitmod
%{_bindir}/sjstat
%{_bindir}/smail
%{_mandir}/man1/sjstat*
#############################################################################

%if %{with pam}
%files -f pam.files pam_slurm
%defattr(-,root,root)
%endif
#############################################################################

%if %{with slurmrestd}
%files slurmrestd
%{_sbindir}/slurmrestd
%{_unitdir}/slurmrestd.service
%endif
#############################################################################

%pre

%post
/sbin/ldconfig
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sacct}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sacctmgr}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,salloc}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sattach}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sbatch}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sbcast}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,scancel}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,scontrol}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,scrontab}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sdiag}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sinfo}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,slurmrestd}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sprio}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,squeue}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sreport}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,srun}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sshare}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,sstat}
ln -sf %{_datadir}/bash-completion/completions/{slurm_completion.sh,strigger}

%preun

%postun
/sbin/ldconfig
if [ $1 -eq 0 ]; then
	rm -f %{_datadir}/bash-completion/completions/sacct
	rm -f %{_datadir}/bash-completion/completions/sacctmgr
	rm -f %{_datadir}/bash-completion/completions/salloc
	rm -f %{_datadir}/bash-completion/completions/sattach
	rm -f %{_datadir}/bash-completion/completions/sbatch
	rm -f %{_datadir}/bash-completion/completions/sbcast
	rm -f %{_datadir}/bash-completion/completions/scancel
	rm -f %{_datadir}/bash-completion/completions/scontrol
	rm -f %{_datadir}/bash-completion/completions/scrontab
	rm -f %{_datadir}/bash-completion/completions/sdiag
	rm -f %{_datadir}/bash-completion/completions/sinfo
	rm -f %{_datadir}/bash-completion/completions/slurmrestd
	rm -f %{_datadir}/bash-completion/completions/sprio
	rm -f %{_datadir}/bash-completion/completions/squeue
	rm -f %{_datadir}/bash-completion/completions/sreport
	rm -f %{_datadir}/bash-completion/completions/srun
	rm -f %{_datadir}/bash-completion/completions/sshare
	rm -f %{_datadir}/bash-completion/completions/sstat
	rm -f %{_datadir}/bash-completion/completions/strigger
fi

%post sackd
%systemd_post sackd.service
%preun sackd
%systemd_preun sackd.service
%postun sackd
%systemd_postun_with_restart sackd.service

%post slurmctld
%systemd_post slurmctld.service
%preun slurmctld
%systemd_preun slurmctld.service
%postun slurmctld
%systemd_postun slurmctld.service

%post slurmd
%systemd_post slurmd.service
%preun slurmd
%systemd_preun slurmd.service
%postun slurmd
%systemd_postun slurmd.service

%post slurmdbd
%systemd_post slurmdbd.service
%preun slurmdbd
%systemd_preun slurmdbd.service
%postun slurmdbd
%systemd_postun slurmdbd.service
%if %{defined patch}
%changelog
* %(date "+%a %b %d %Y") %{?packager} - %{version}-%{release}
- Includes patch: %{patch}
%endif

#############################################################################

%changelog
* Wed Apr 30 2025 Paul Edmon <pedmon@cfa.harvard.edu> 24.11.4-1fasrc01
- Rebase onto 24.11.4

* Tue Apr 1 2025 Paul Edmon <pedmon@cfa.harvard.edu> 24.11.3-1fasrc01
- Rebase onto 24.11.3

* Wed Feb 26 2025 Paul Edmon <pedmon@cfa.harvard.edu> 24.11.2-1fasrc01
- Rebase onto 24.11.2

* Fri Jan 24 2025 Paul Edmon <pedmon@cfa.harvard.edu> 24.11.1-1fasrc01
- Rebase onto 24.11.1

* Wed Oct 30 2024 Paul Edmon <pedmon@cfa.harvard.edu> 24.05.4-1fasrc01
- Rebase onto 24.05.4

* Fri Aug 30 2024 Paul Edmon <pedmon@cfa.harvard.edu> 24.05.3-1fasrc01
- Rebase onto 24.05.3

* Thu Jun 20 2024 Paul Edmon <pedmon@cfa.harvard.edu> 23.11.8-1fasrc01
- Rebase onto 23.11.8

* Fri Feb 23 2024 Paul Edmon <pedmon@cfa.harvard.edu> 23.11.4-1fasrc01
- Rebase onto 23.11.4

* Fri Jan 26 2024 Paul Edmon <pedmon@cfa.harvard.edu> 23.11.3-1fasrc01
- Rebase onto 23.11.3

* Thu Dec 14 2023 Paul Edmon <pedmon@cfa.harvard.edu> 23.02.7-1fasrc01
- Rebase onto 23.02.7

* Thu Oct 12 2023 Paul Edmon <pedmon@cfa.harvard.edu> 23.02.6-1fasrc01
- Rebase onto 23.02.6

* Tue Sep 19 2023 Paul Edmon <pedmon@cfa.harvard.edu> 23.02.5-1fasrc01
- Rebase onto 23.02.5

* Mon Aug 21 2023 Paul Edmon <pedmon@cfa.harvard.edu> 23.02.4-1fasrc01
- Rebase onto 23.02.4

* Fri Jun 16 2023 Paul Edmon <pedmon@cfa.harvard.edu> 23.02.3-1fasrc01
- Rebase onto 23.02.3

* Wed Jun 14 2023 Paul Edmon <pedmon@cfa.harvard.edu> 22.05.9-1fasrc01
- Rebase onto 22.05.9

* Wed Jan 4 2023 Paul Edmon <pedmon@cfa.harvard.edu> 22.05.7-1fasrc01
- Rebase 22.05.7

* Wed Nov 23 2022 Paul Edmon <pedmon@cfa.harvard.edu> 22.05.6-1fasrc01
- Rebase onto 22.05.6

* Tue Aug 30 2022 Paul Edmon <pedmon@cfa.harvard.edu> 22.05.3-1fasrc01
- Rebase onto 22.05.3
- Activate REST API

* Tue Jul 5 2022 Paul Edmon <pedmon@cfa.harvard.edu> 22.05.2-1fasrc01
- Rebase onto 22.05.2

* Fri May 6 2022 Paul Edmon <pedmon@cfa.harvard.edu> 21.08.8-2fasrc01
- Rebase onto 21.08.8-2

* Thu May 5 2022 Paul Edmon <pedmon@cfa.harvard.edu> 21.08.8-1fasrc01
- Rebase onto 21.08.8

* Fri Feb 25 2022 Paul Edmon <pedmon@cfa.harvard.edu> 21.08.6-1fasrc01
- Rebase onto 21.08.6

* Mon Jan 3 2022 Paul Edmon <pedmon@cfa.harvard.edu> 21.08.5-1fasrc01
- Rebase onto 21.08.5

* Thu Dec 16 2021 Paul Edmon <pedmon@cfa.harvard.edu> 21.08.4-1fasrc01
- Rebase onto 21.08.4
- Dropping patch for 10625 as its fixed in 21.08.5 and not an essential
- patch

* Mon Oct 25 2021 Paul Edmon <pedmon@cfa.harvard.edu> 21.08.2-1fasrc02
- Adding patch for bug 10625

* Thu Oct 21 2021 Paul Edmon <pedmon@cfa.harvard.edu> 21.08.2-1fasrc01
- Rebase onto 21.08.2

* Tue May 25 2021 Paul Edmon <pedmon@cfa.harvard.edu> 20.11.7-1fasrc01
- Rebase onto 20.11.7

* Fri Mar 19 2021 Paul Edmon <pedmon@cfa.harvard.edu> 20.11.5-1fasrc01
- Rebase onto 20.11.5

* Tue Feb 23 2021 Paul Edmon <pedmon@cfa.harvard.edu> 20.11.4-1fasrc01
- Rebase onto 20.11.4
- Dropping patch for bug 10824.

* Fri Feb 12 2021 Paul Edmon <pedmon@cfa.harvard.edu> 20.11.3-1fasrc02
- Applying bug10824_2011_3_debug_v1.patch from:
- https://bugs.schedmd.com/show_bug.cgi?id=10824

* Mon Jan 25 2021 Paul Edmon <pedmon@cfa.harvard.edu> 20.11.3-1fasrc01
- Rebase onto 20.11.3

* Fri Jan 8 2021 Paul Edmon <pedmon@cfa.harvard.edu> 20.11.2-1fasrc02
- Pursuiant to bug 10383 we are going to rebase to the bde072c607 commit
- of the 20.11 release.  We will call this 20.11.2-1fasrc02.

* Mon Jan 4 2021 Paul Edmon <pedmon@cfa.harvard.edu> 20.11.2-1fasrc01
- Rebase onto 20.11.2

* Mon Dec 14 2020 Paul Edmon <pedmon@cfa.harvard.edu> 20.11.1-1fasrc01
- Rebase onto 20.11.1

* Fri Nov 13 2020 Justin Riley <justin_riley@harvard.edu> 20.02.6-1fasrc01
- Rebase onto 20.02.6

* Fri Sep 11 2020 Paul Edmon <pedmon@cfa.harvard.edu> 20.02.5-1fasrc01
- Rebase onto 20.02.5

* Tue Sep 8 2020 Paul Edmon <pedmon@cfa.harvard.edu> 20.02.4-1fasrc01
- Rebase onto 20.02.4

* Tue Jun 16 2020 Paul Edmon <pedmon@cfa.harvard.edu> 20.02.3-1fasrc01
- Rebase onto 20.02.3

* Fri May 1 2020 Paul Edmon <pedmon@cfa.harvard.edu> 20.02.2-1fasrc01
- Rebase onto 20.02.2

* Thu Apr 16 2020 Paul Edmon <pedmon@cfa.harvard.edu> 20.02.1-1fasrc01
- Rebase onto 20.20.1

* Wed Jan 8 2020 Paul Edmon <pedmon@cfa.harvard.edu> 19.05.5-1fasrc01
- Rebase onto 19.05.5

* Thu Nov 21 2019 Paul Edmon <pedmon@cfa.harvard.edu> 19.05.4-1fasrc01
- Rebase onto 19.05.4

* Tue Oct 22 2019 Paul Edmon <pedmon@cfa.harvard.edu> 19.05.3-2fasrc01
- Rebase onto 19.05.3-2

* Thu Jul 11 2019 Paul Edmon <pedmon@cfa.harvard.edu> 19.05.1-2fasrc01
- Rebase onto 19.05.1-2
- We will start using the builtin X11.
- Forked specs for GPU and nonGPU hosts.

* Mon Apr 29 2019 Paul Edmon <pedmon@cfa.harvard.edu> 18.08.7-1fasrc01
- Rebase onto 18.08.7

* Wed Apr 3 2019 Paul Edmon <pedmon@cfa.harvard.edu> 18.08.6-2fasrc01
- Rebase onto 18.08.6-2

* Thu Feb 21 2019 Paul Edmon <pedmon@cfa.harvard.edu> 18.08.5-2fasrc01
- Rebase onto 18.08.5-2

* Tue Oct 30 2018 Paul Edmon <pedmon@cfa.harvard.edu> 17.11.12-1fasrc01
- Rebase onto 17.11.9-2
- We are going to neuter the restart here for the services as we want
- to control that by hand or by puppet.  This is due to the fact that
- it can create problems when doing upgrades.  This is under postun.

* Mon Aug 13 2018 Paul Edmon <pedmon@cfa.harvard.edu> 17.11.9-2fasrc01
- Rebase onto 17.11.9-2
- Adding PMIx support

* Thu May 31 2018 Paul Edmon <pedmon@cfa.harvard.edu> 17.11.7-1fasrc01
- Rebase onto 17.11.7

* Mon Mar 19 2018 Paul Edmon <pedmon@cfa.harvard.edu> 17.11.5-1fasrc01
- Rebase onto 17.11.5

* Thu Mar 1 2018 Paul Edmon <pedmon@cfa.harvard.edu> 17.11.4-1fasrc01
- Rebase onto 17.11.4

* Wed Feb 7 2018 Paul Edmon <pedmon@cfa.harvard.edu> 17.11.3-2fasrc01
- Rebase onto 17.11.3-2
- Added dependency on libssh2-devel in order to enable X11 but disabled
- X11 due to incompatibility with CentOS 6.

* Fri Jan 5 2018 Paul Edmon <pedmon@cfa.harvard.edu> 17.11.2-1fasrc01
- Rebase onto 17.11.2

* Tue Jan 2 2018 Paul Edmon <pedmon@cfa.harvard.edu> 17.11.1-2fasrc01
- Rebase onto 17.11.1-2

* Fri Dec 1 2017 Paul Edmon <pedmon@cfa.harvard.edu> 17.11.0-1fasrc01
- Rebase onto 17.11.0

* Fri Nov 3 2017 Paul Edmon <pedmon@cfa.harvard.edu> 17.02.9-1fasrc01
- Rebase onto 17.02.9

* Fri Oct 20 2017 Paul Edmon <pedmon@cfa.harvard.edu> 17.02.8-1fasrc01
- Rebase onto 17.02.8

* Fri Aug 18 2017 Paul Edmon <pedmon@cfa.harvard.edu> 17.02.7-1fasrc01
- Rebase onto 17.02.7

* Thu Jul 6 2017 Paul Edmon <pedmon@cfa.harvard.edu> 17.02.6-1fasrc01
- Rebase onto 17.02.6

* Fri Jun 23 2017 Paul Edmon <pedmon@cfa.harvard.edu> 17.02.5-1fasrc01
- Rebase onto 17.02.5

* Wed Jun 7 2017 Paul Edmon <pedmon@cfa.harvard.edu> 17.02.4-1fasrc01
- Rebase onto 17.02.4

* Thu May 11 2017 Paul Edmon <pedmon@cfa.harvard.edu> 17.02.3-1fasrc01
- Rebase onto 17.02.3

* Wed Feb 1 2017 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.9-1fasrc01
- Rebase onto 16.05.9

* Thu Jan 5 2017 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.8-1fasrc01
- Rebase onto 16.05.8

* Tue Dec 13 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.7-1fasrc01
- Rebase onto 16.05.7

* Mon Oct 31 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.6-1fasrc01
- Happy Reformation Day!
- Rebase onto 16.05.6

* Thu Sep 29 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.5-1fasrc01
- Rebase onto 16.05.5

* Thu Aug 18 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.4-1fasrc01
- Rebase onto 16.05.4

* Wed Jul 27 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.3-1fasrc01
- Rebase onto 16.05.3
- Dropped 65b4f283ef2a908b6e3e8921acf62dad73528f00.patch as it is fixed

* Mon Jul 11 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.2-1fasrc02
- 65b4f283ef2a908b6e3e8921acf62dad73528f00.patch for bug
- https://bugs.schedmd.com/show_bug.cgi?id=2885
- Fixed in 16.05.3

* Fri Jul 8 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.2-1fasrc01
- Rebase onto 16.05.2

* Wed Jun 1 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.0-1fasrc01
- Rebase onto 16.05.0

* Fri May 13 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.0-0rc2fasrc01
- Rebase onto 16.05.0rc2

* Wed May 4 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.0-0rc1fasrc01
- Rebase onto 16.05.0rc1

* Wed Apr 20 2016 Paul Edmon <pedmon@cfa.harvard.edu> 16.05.0-0pre2fasrc01
- Rebase onto 16.05.0-0pre2
- Dropped all bug fixes for 15.08

* Thu Apr 7 2016 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.10-1fasrc01
- Rebase onto 15.08.10
- Also included bug fix: https://bugs.schedmd.com/show_bug.cgi?id=2573
- This bug will be fully fixed in 15.08.11

* Wed Mar 30 2016 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.9-1fasrc01
- Rebase onto 15.08.9

* Fri Feb 19 2016 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.8-1fasrc01
- Rebase onto 15.08.8

* Thu Jan 21 2016 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.7-1fasrc01
- Rebase onto 15.08.7

* Tue Jan 5 2016 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.6-1fasrc01
- Rebase onto 15.08.6
- Bug 2243 fixed in this release.

* Tue Dec 15 2015 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.5-1fasrc02
- Replaced src/common/xlua.c pursuiant to bug 2243
- http://bugs.schedmd.com/show_bug.cgi?id=2243
- Should be fixed in next minor release.

* Mon Dec 14 2015 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.5-1fasrc01
- Rebase onto 15.08.5 release.

* Mon Nov 16 2015 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.4-1fasrc01
- Rebase onto 15.08.4 release.

* Thu Nov 5 2015 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.3-1fasrc01
- Rebase onto 15.08.3 release.

* Mon Oct 26 2015 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.2-1fasrc01
- Rebase onto 15.08.2 release.
- Turned on hwloc

* Tue Oct 6 2015 Paul Edmon <pedmon@cfa.harvard.edu> 15.08.1-1fasrc01
- Rebase onto 15.08.1 release.
- Dropped all patches as all are fixed in this version.

* Thu Aug 13 2015 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.8-1fasrc03
- Removed Patch ad9c2413a735a6b15a0133ac5068d546c52de9a1.patch
- For reason see previous bug.
- Added Patch bug_1850.patch
- See: http://bugs.schedmd.com/show_bug.cgi?id=1850

* Thu Jul 9 2015 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.8-1fasrc02
- Patch ad9c2413a735a6b15a0133ac5068d546c52de9a1.patch
- See: http://bugs.schedmd.com/show_bug.cgi?id=1794

* Wed Jul 8 2015 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.8-1fasrc01
- Rebase onto 14.11.8 release
- archive patches no longer needed.

* Tue May 26 2015 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.7-1fasrc01
- Rebase onto 14.11.7 release
- purge.patch and deadlock.patch no longer needed.

* Tue Apr 28 2015 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.4-1fasrc09
- Copied from other slurm branch as we never upgraded to 14.11.5 on the production branch
- Added patches related to http://bugs.schedmd.com/show_bug.cgi?id=1576
- Patch list: purge.patch, archive_1411.patch, deadlock.patch, archive_1411.patch2, archive_1411.patch3
- Patches can be dropped at 15.08 release

* Tue Mar 24 2015 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.5-1fasrc02
- Changed compiler CFLAGS=-ggdb -O0 at the suggestion of:
- http://bugs.schedmd.com/show_bug.cgi?id=1557#c13

* Fri Mar 20 2015 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.5-1fasrc01
- Rebase onto 14.11.5 release

* Fri Feb 13 2015 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.4-1fasrc01
- Rebase onto 14.11.4 release

* Fri Jan 9 2015 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.3-1fasrc01
- Rebase onto 14.11.3 release

* Wed Dec 3 2014 Paul Edmon <pedmon@cfa.harvard.edu> 14.11.1-1fasrc01
- Rebase onto 14.11.1 release
- Dropped all old patches as this is a major release change.

* Thu Sep 25 2014 Paul Edmon <pedmon@cfa.harvard.edu> 14.03.8-1fasrc01
- Rebase onto 14.03.8 release
- Dropped crufty message patch but kept lua patch pending 14.11 release.

* Tue Jun 17 2014 John Morrissey <jmorrissey@fas.harvard.edu> 14.03.4-2fasrc00
- Rebase onto 14.03.4-2 release
- Drop all local patches; they've been merged upstream except for
  bf_config.patch, which provided the bf_yield_{interval,sleep}
  SchedulerParameters that we don't seem to use.

* Thu May 15 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.9-1fasrc03
- Add slurm-2261d39394.patch for http://bugs.schedmd.com/show_bug.cgi?id=798

* Mon Apr 21 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.9-1fasrc02
- Add bf_config.patch.

* Thu Apr 10 2014 Paul Edmon <pedmon@cfa.harvard.edu> 2.6.9-1fasrc01
- Upgrade to upstream release 2.6.9.
- Add partition_depth.patch which is partition_job_depth.patch for 2.6.9
- Drop bug_595.patch, slurm-8fb863f9dd.patch, and slurm-dd4aa1c3c4.patch;
  they're included upstream in this release.

* Thu Apr 3 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.5-1fasrc08
- Add slurm-8fb863f9dd.patch, slurm-dd4aa1c3c4.patch
  bugs.schedmd.com/show_bug.cgi?id=616

* Thu Mar 20 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.5-1fasrc07
- Add fix-cpuload-updates.patch

* Wed Mar 19 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.5-1fasrc06
- Add 08f0f57cc18824d0984bbbbba39ad27d4e796a62.patch
  http://bugs.schedmd.com/show_bug.cgi?id=630

* Mon Mar 10 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.5-1fasrc05
- Add bf_max_job_start.patch, from upstream commit
  1b0c4a33590c24a6509750f48b2108c0baea4fbe

* Wed Mar 5 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.5-1fasrc04
- Add patches for SchedMD bugs 534 and 595.

* Wed Feb 12 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.5-1fasrc03
- Rebuild to make sure we're building against a (locked) compute image.

* Mon Feb 10 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.5-1fasrc02
- Add partition_job_depth.patch from SchedMD.
  https://groups.google.com/forum/#!topic/slurm-devel/b5xoAIu0W-4

* Thu Jan 23 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.5-1fasrc01
- Increase the thread stack size to accomodate the larger PW_BUF_SIZE,
  preventing stack corruption during operations like reconfig.

* Sat Jan 11 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.5-1fasrc00
- Upgrade to upstream 2.6.5 release
  - Remove all of our local patches except larger-pw-buf-size.patch; they've
    been merged upstream.

* Fri Jan 10 2014 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.3-1fasrc03
- Add larger-pw-buf-size.patch
- Remove bf_max_job_cpus.patch; it wouldn't have been a huge win, and
  bf_max_job_user=100 was a huge improvement.
- More build fixes for mock
  - Need BuildRequires on chkconfig, since it owns /etc/init.d. The init
    script isn't packaged otherwise.
  - Force MySQL support.
  - BuildRequires on gtk2-devel so we build sview.

* Tue Dec 3 2013 John Morrissey <jmorrissey@fas.harvard.edu> 2.6.3-1fasrc02
- Add bf_max_job_cpus.patch

* Tue Oct 22 2013 John Morrissey <jmorrissey@fas.harvard.edu>
- Add bug447-attachment-475-fix-proctrack-cgroup-race.patch

* Sun Oct 20 2013 John Morrissey <jmorrissey@fas.harvard.edu>
- Add slurm-ea1b316c60ad2863bdc39bb2610229024bce17fa.patch, from
  http://bugs.schedmd.com/show_bug.cgi?id=470

* Tue Oct 15 2013 John Morrissey <jmorrissey@fas.harvard.edu>
- Add patch0, patch1 from SchedMD bug 445.
- Build with Lua support by default, since we use a Lua job_submit script.

* Wed Jun 26 2013 Morris Jette <jette@schedmd.com> 14.03.0-0pre1
Various cosmetic fixes for rpmlint errors

