#Module-Specific definitions
%define mod_name mod_cguard
%define mod_conf B18_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Connection Guard Module for Apache 2
Name:		apache-%{mod_name}
Version:	0.1
Release:	%mkrel 1
Group:		System/Servers
License:	Apache License
URL:		http://httpd.renatasystems.org/mod_cguard/
Source0:	http://httpd.renatasystems.org/mod_cguard/%{mod_name}-%{version}.tgz
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache-mpm-prefork >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file

%description
Simple and flexible connection limiter

%prep

%setup -q -n %{mod_name}

cp %{SOURCE1} %{mod_conf}

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type d -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

%{_sbindir}/apxs -c -Wc,"-Wall -g" -DCGUARD_DEBUG mod_cguard.c
mv .libs/mod_cguard.so mod_cguard-debug.so 

rm -rf .libs
rm -f *.la *.*lo *.o

%{_sbindir}/apxs -c -Wc,"-Wall -g" mod_cguard.c
mv .libs/mod_cguard.so mod_cguard.so 


%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules

install -m0755 mod_cguard.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0755 mod_cguard-debug.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_cguard.so 
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_cguard-debug.so 
