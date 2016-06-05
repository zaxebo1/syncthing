%global debug_package %{nil}

%global provider        github
%global provider_tld    com
%global project         thejerf
%global repo            suture

%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          f617879c797f06948b1075874e4aa32fa197bd24
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global goroot /usr/lib/golang


%ifarch x86_64
%global dynlinkdir linux_amd64_dynlink
%endif

%ifarch %{ix86}
%global dynlinkdir linux_386_dynlink
%endif


Name:           golang-%{provider}-%{project}-%{repo}
Version:        0~%{shortcommit}
Release:        1%{?dist}
Summary:        Supervisor trees for Go
License:        ???
URL:            https://%{provider_prefix}

Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz


ExclusiveArch:  %{go_arches}


BuildRequires:  golang

%if 0%{?fedora} > 23
BuildRequires:  golang-shared
%endif


%description
%{summary}


%if 0%{?fedora} > 23
%package        lib
Summary:        %{summary}

Requires:       golang-shared

%description    lib
%{summary}

This package contains the shared go library.
%endif


%package        devel
Summary:        %{summary}

BuildArch:      noarch
Provides:       golang(%{import_path}) = %{version}-%{release}

%description    devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.


%prep
%setup -q -n %{repo}-%{commit}


%build
%if 0%{?fedora} > 23
mkdir -p _build/src/%{provider}.%{provider_tld}/%{project}/

pushd _build/src/%{provider}.%{provider_tld}/%{project}/
ln -s ../../../../ %{repo}
popd

GOPATH=$(pwd)/_build:%{gopath}
export GOPATH

go install -buildmode shared -linkshared %{provider}.%{provider_tld}/%{project}/%{repo}
%endif


%install
%if 0%{?fedora} > 23
# install built files
mkdir -p %{buildroot}/usr/lib/golang/pkg/%{dynlinkdir}

cp _build/pkg/%{dynlinkdir}/*.so %{buildroot}/usr/lib/golang/pkg/%{dynlinkdir}/
cp -R _build/pkg/%{dynlinkdir}/%{provider}.%{provider_tld} %{buildroot}/usr/lib/golang/pkg/%{dynlinkdir}/


# cleanup of build files
rm -r _build
%endif

# install source and unit test files
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}/." >> devel.file-list
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done

sort -u -o devel.file-list devel.file-list


%if 0%{?fedora} > 23
%files          lib
%license LICENSE
%doc README.md
/usr/lib/golang/pkg/%{dynlinkdir}/*.so
/usr/lib/golang/pkg/%{dynlinkdir}/%{provider}.%{provider_tld}/%{project}
%endif


%files          devel -f devel.file-list
%license LICENSE
%doc README.md
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}


%changelog
* Wed May 18 2016 Fabio Valentini <decathorpe@gmail.com> - 0~f617879-1
- First package for Fedora

