Name:		slurm
Version:	20.11.3
%define rel	1
Release:	%{rel}fasrc01%{?dist}
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
Patch0:         bug10824_2011_3_debug_v1.patch

# build options		.rpmmacros options	change to default action
# ====================  ====================	========================
# --prefix		%_prefix path		install path for commands, libraries, etc.
# --with cray		%_with_cray 1		build for a Cray Aries system
# --with cray_network	%_with_cray_network 1	build for a non-Cray system with a Cray network
# --with cray_shasta	%_with_cray_shasta 1	build for a Cray Shasta system
# --with slurmrestd	%_with_slurmrestd 1	build slurmrestd
# --with slurmsmwd      %_with_slurmsmwd 1      build slurmsmwd
# --without debug	%_without_debug 1	don't compile with debugging symbols
# --with hdf5		%_with_hdf5 path	require hdf5 support
# --with hwloc		%_with_hwloc 1		require hwloc support
# --with lua		%_with_lua path		build Slurm lua bindings
# --with mysql		%_with_mysql 1		require mysql/mariadb support
# --with numa		%_with_numa 1		require NUMA support
# --without pam		%_without_pam 1		don't require pam-devel RPM to be installed
# --without x11		%_without_x11 1		disable internal X11 support
# --with ucx		%_with_ucx path		require ucx support
# --with pmix		%_with_pmix path	require pmix support

#  Options that are off by default (enable with --with <opt>)
%bcond_with cray
%bcond_with cray_network
%bcond_with cray_shasta
%bcond_with slurmrestd
%bcond_with slurmsmwd
%bcond_with multiple_slurmd
%bcond_with ucx

# These options are only here to force there to be these on the build.
# If they are not set they will still be compiled if the packages exist.
%bcond_with hwloc
%bcond_with mysql
%bcond_with hdf5
%bcond_with lua
%bcond_with numa
%bcond_with pmix

# Use debug by default on all systems
%bcond_without debug

# Options enabled by default
%bcond_without pam
%bcond_without x11

# Disable hardened builds. -z,now or -z,relro breaks the plugin stack
%undefine _hardened_build
%global _hardened_cflags "-Wl,-z,lazy"
%global _hardened_ldflags "-Wl,-z,lazy"

Requires: munge

%{?systemd_requires}
BuildRequires: systemd
BuildRequires: munge-devel munge-libs
BuildRequires: python3
BuildRequires: readline-devel
Obsoletes: slurm-lua slurm-munge slurm-plugins

# fake systemd support when building rpms on other platforms
%{!?_unitdir: %global _unitdir /lib/systemd/systemd}

%define use_mysql_devel %(perl -e '`rpm -q mariadb-devel`; print $?;')

%if %{with mysql}
%if %{use_mysql_devel}
BuildRequires: mysql-devel >= 5.0.0
%else
BuildRequires: mariadb-devel >= 5.0.0
%endif
%endif

%if %{with cray}
BuildRequires: cray-libalpscomm_cn-devel
BuildRequires: cray-libalpscomm_sn-devel
BuildRequires: libnuma-devel
BuildRequires: libhwloc-devel
BuildRequires: cray-libjob-devel
BuildRequires: gtk2-devel
BuildRequires: glib2-devel
BuildRequires: pkg-config
%endif

%if %{with cray_network}
%if %{use_mysql_devel}
BuildRequires: mysql-devel
%else
BuildRequires: mariadb-devel
%endif
BuildRequires: cray-libalpscomm_cn-devel
BuildRequires: cray-libalpscomm_sn-devel
BuildRequires: hwloc-devel
BuildRequires: gtk2-devel
BuildRequires: glib2-devel
BuildRequires: pkgconfig
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

%if %{with lua}
BuildRequires: pkgconfig(lua) >= 5.1.0
%endif

%if %{with hwloc}
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
%global pmix_version %(rpm -q pmix --qf "%{VERSION}")
%endif

%if %{with ucx} && "%{_with_ucx}" == "--with-ucx"
BuildRequires: ucx-devel
%global ucx_version %(rpm -q ucx-devel --qf "%{VERSION}")
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

%package slurmctld
Summary: Slurm controller daemon
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
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
Obsoletes: slurm-sql
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
Obsoletes: slurm-sjobexit slurm-sjstat slurm-seff
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
Obsoletes: pam_slurm
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

%if %{with slurmsmwd}
%package slurmsmwd
Summary: support daemons and software for the Cray SMW
Group: System Environment/Base
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: craysmw
%description slurmsmwd
support daemons and software for the Cray SMW.  Includes slurmsmwd which
notifies slurm about failed nodes.
%endif

#############################################################################

%prep
# when the rel number is one, the tarball filename does not include it
%setup -n %{slurm_source_dir}
%patch0 -p1

%build
%configure \
	%{?_without_debug:--disable-debug} \
	%{?_with_pam_dir} \
	%{?_with_cpusetdir} \
	%{?_with_mysql_config} \
	%{?_with_ssl} \
	%{?_without_cray:--enable-really-no-cray}\
	%{?_with_cray_network:--enable-cray-network}\
	%{?_with_multiple_slurmd:--enable-multiple-slurmd} \
	%{?_with_pmix} \
	%{?_with_freeipmi} \
	%{?_with_hdf5} \
	%{?_with_shared_libslurm} \
	%{!?_with_slurmrestd:--disable-slurmrestd} \
	%{?_without_x11:--disable-x11} \
	%{?_with_ucx} \
	%{?_with_cflags}

make %{?_smp_mflags}

%install

# Ignore redundant standard rpaths and insecure relative rpaths,
# for RHEL based distros which use "check-rpaths" tool.
export QA_RPATHS=0x5

# Strip out some dependencies

cat > find-requires.sh <<'EOF'
exec %{__find_requires} "$@" | egrep -v '^libpmix.so|libevent|libnvidia-ml'
EOF
chmod +x find-requires.sh
%global _use_internal_dependency_generator 0
%global __find_requires %{_builddir}/%{buildsubdir}/find-requires.sh

rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
make install-contrib DESTDIR=%{buildroot}

install -D -m644 etc/slurmctld.service %{buildroot}/%{_unitdir}/slurmctld.service
install -D -m644 etc/slurmd.service    %{buildroot}/%{_unitdir}/slurmd.service
install -D -m644 etc/slurmdbd.service  %{buildroot}/%{_unitdir}/slurmdbd.service

%if %{with slurmrestd}
install -D -m644 etc/slurmrestd.service  %{buildroot}/%{_unitdir}/slurmrestd.service
%endif

# Do not package Slurm's version of libpmi on Cray systems in the usual location.
# Cray's version of libpmi should be used. Move it elsewhere if the site still
# wants to use it with other MPI stacks.
%if %{with cray} || %{with cray_shasta}
   mkdir %{buildroot}/%{_libdir}/slurmpmi
   mv %{buildroot}/%{_libdir}/libpmi* %{buildroot}/%{_libdir}/slurmpmi
%endif

%if %{with cray}
   install -D -m644 contribs/cray/plugstack.conf.template %{buildroot}/%{_sysconfdir}/plugstack.conf.template
   install -D -m644 contribs/cray/slurm.conf.template %{buildroot}/%{_sysconfdir}/slurm.conf.template
   mkdir -p %{buildroot}/opt/modulefiles/slurm
   test -f contribs/cray/opt_modulefiles_slurm &&
      install -D -m644 contribs/cray/opt_modulefiles_slurm %{buildroot}/opt/modulefiles/slurm/%{version}-%{rel}
   echo -e '#%Module\nset ModulesVersion "%{version}-%{rel}"' > %{buildroot}/opt/modulefiles/slurm/.version
%else
   rm -f contribs/cray/opt_modulefiles_slurm
   rm -f %{buildroot}/%{_sysconfdir}/plugstack.conf.template
   rm -f %{buildroot}/%{_sysconfdir}/slurm.conf.template
   rm -f %{buildroot}/%{_sbindir}/capmc_suspend
   rm -f %{buildroot}/%{_sbindir}/capmc_resume
   rm -f %{buildroot}/%{_sbindir}/slurmconfgen.py
%endif

%if %{with slurmsmwd}
   install -D -m644 contribs/cray/slurmsmwd/slurmsmwd.service %{buildroot}/%{_unitdir}/slurmsmwd.service
%else
   rm -f %{buildroot}/%{_sbindir}/slurmsmwd
   rm -f contribs/cray/slurmsmwd/slurmsmwd.service
%endif

install -D -m644 etc/cgroup.conf.example %{buildroot}/%{_sysconfdir}/cgroup.conf.example
install -D -m644 etc/slurm.conf.example %{buildroot}/%{_sysconfdir}/slurm.conf.example
install -D -m600 etc/slurmdbd.conf.example %{buildroot}/%{_sysconfdir}/slurmdbd.conf.example
install -D -m755 contribs/sjstat %{buildroot}/%{_bindir}/sjstat

# Delete unpackaged files:
find %{buildroot} -name '*.a' -exec rm {} \;
find %{buildroot} -name '*.la' -exec rm {} \;
rm -f %{buildroot}/%{_libdir}/slurm/job_submit_defaults.so
rm -f %{buildroot}/%{_libdir}/slurm/job_submit_logging.so
rm -f %{buildroot}/%{_libdir}/slurm/job_submit_partition.so
rm -f %{buildroot}/%{_libdir}/slurm/auth_none.so
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

# Build man pages that are generated directly by the tools
rm -f %{buildroot}/%{_mandir}/man1/sjobexitmod.1
%{buildroot}/%{_bindir}/sjobexitmod --roff > %{buildroot}/%{_mandir}/man1/sjobexitmod.1
rm -f %{buildroot}/%{_mandir}/man1/sjstat.1
%{buildroot}/%{_bindir}/sjstat --roff > %{buildroot}/%{_mandir}/man1/sjstat.1

# Build conditional file list for main package
LIST=./slurm.files
touch $LIST
test -f %{buildroot}/%{_libexecdir}/slurm/cr_checkpoint.sh   &&
  echo %{_libexecdir}/slurm/cr_checkpoint.sh	        >> $LIST
test -f %{buildroot}/%{_libexecdir}/slurm/cr_restart.sh      &&
  echo %{_libexecdir}/slurm/cr_restart.sh	        >> $LIST
test -f %{buildroot}/%{_sbindir}/capmc_suspend		&&
  echo %{_sbindir}/capmc_suspend			>> $LIST
test -f %{buildroot}/%{_sbindir}/capmc_resume		&&
  echo %{_sbindir}/capmc_resume				>> $LIST
test -f %{buildroot}/%{_bindir}/netloc_to_topology		&&
  echo %{_bindir}/netloc_to_topology			>> $LIST

test -f %{buildroot}/opt/modulefiles/slurm/%{version}-%{rel} &&
  echo /opt/modulefiles/slurm/%{version}-%{rel} >> $LIST
test -f %{buildroot}/opt/modulefiles/slurm/.version &&
  echo /opt/modulefiles/slurm/.version >> $LIST


LIST=./example.configs
touch $LIST
%if %{with cray}
   test -f %{buildroot}/%{_sbindir}/slurmconfgen.py	&&
	echo %{_sbindir}/slurmconfgen.py		>>$LIST
%endif

# Make pkg-config file
mkdir -p %{buildroot}/%{_libdir}/pkgconfig
cat >%{buildroot}/%{_libdir}/pkgconfig/slurm.pc <<EOF
includedir=%{_prefix}/include
libdir=%{_libdir}

Cflags: -I\${includedir}
Libs: -L\${libdir} -lslurm
Description: Slurm API
Name: %{name}
Version: %{version}
EOF

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

%files -f slurm.files
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
%if %{with cray}
%dir /opt/modulefiles/slurm
%endif
#############################################################################

%files -f example.configs example-configs
%defattr(-,root,root,0755)
%dir %{_sysconfdir}
%if %{with cray}
%config %{_sysconfdir}/plugstack.conf.template
%config %{_sysconfdir}/slurm.conf.template
%endif
%config %{_sysconfdir}/cgroup.conf.example
%config %{_sysconfdir}/slurm.conf.example
%config %{_sysconfdir}/slurmdbd.conf.example
#############################################################################

%files devel
%defattr(-,root,root)
%dir %attr(0755,root,root)
%dir %{_prefix}/include/slurm
%{_prefix}/include/slurm/*
%dir %{_libdir}/pkgconfig
%{_libdir}/pkgconfig/slurm.pc
#############################################################################

%files perlapi
%defattr(-,root,root)
%{_perldir}/Slurm.pm
%{_perldir}/Slurm/Bitstr.pm
%{_perldir}/Slurm/Constant.pm
%{_perldir}/Slurm/Hostlist.pm
%{_perldir}/Slurm/Stepctx.pm
%{_perldir}/auto/Slurm/Slurm.so
%{_perldir}/Slurmdb.pm
%{_perldir}/auto/Slurmdb/Slurmdb.so
%{_perldir}/auto/Slurmdb/autosplit.ix
%{_perlman3dir}/Slurm*

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
%if %{with cray} || %{with cray_shasta}
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

%if %{with slurmsmwd}
%files slurmsmwd
%{_sbindir}/slurmsmwd
%{_unitdir}/slurmsmwd.service
%endif
#############################################################################

%pre

%post
/sbin/ldconfig

%preun

%postun
/sbin/ldconfig

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

#############################################################################

%changelog
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
