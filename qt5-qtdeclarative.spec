%global __provides_exclude_from ^%{_qt5_archdatadir}/qml/.*\\.so$

Name:             qt5-qtdeclarative
Version:          5.11.1
Release:          6
License:          LGPLv2 with exceptions or GPLv3 with exceptions
Summary:          Qt5 module for declarative framework
Url:              http://www.qt.io
Source0:          https://download.qt.io/new_archive/qt/5.11/%{version}/submodules/qtdeclarative-everywhere-src-%{version}.tar.xz
Source1:          qv4global_p-multilib.h
Patch0001:        qtdeclarative-opensource-src-5.11.0-no_sse2.patch
Obsoletes:        qt5-qtjsbackend < 5.2.0 qt5-qtdeclarative-render2d < 5.7.1-10
BuildRequires:    gcc-c++ qt5-rpm-macros >= %{version} qt5-qtbase-devel >= %{version}
BuildRequires:    qt5-qtbase-private-devel qt5-qtxmlpatterns-devel >= %{version} python3 python2
%{?_qt5:Requires: %{_qt5} = %{_qt5_version}}

%if 0%{?tests}
BuildRequires: dbus-x11 mesa-dri-drivers time xorg-x11-server-Xvfb
%endif

%description
This package contains base tools, like string, xml, and network handling.

%package devel
Summary:          Library and header files of %{name}
Requires:         %{name} = %{version}-%{release} qt5-qtbase-devel
Provides:         %{name}-private-devel = %{version}-%{release}
Provides:         %{name}-static = %{version}-%{release} %{name}-examples = %{version}-%{release}
Obsoletes:        qt5-qtjsbackend-devel < 5.2.0 qt5-qtdeclarative-render2d-devel < 5.7.1-10
Obsoletes:        %{name}-static < %{version}-%{release} %{name}-examples < %{version}-%{release}

%description devel
%{name}-devel provides libraries and header files for %{name}.

%prep
%setup -q -n qtdeclarative-everywhere-src-%{version}

%build

%qmake_qt5

%make_build

%install
%make_install INSTALL_ROOT=%{buildroot}

%ifarch x86_64
  pushd %{buildroot}%{_qt5_headerdir}/QtQml/%{version}/QtQml/private
  mv qv4global_p.h qv4global_p-%{__isa_bits}.h
  popd
  install -p -m644 -D %{SOURCE1} %{buildroot}%{_qt5_headerdir}/QtQml/%{version}/QtQml/private/qv4global_p.h
%endif

install -d %{buildroot}%{_bindir}
pushd %{buildroot}%{_qt5_bindir}
for file in * ; do
  case "${file}" in
    qmlplugindump|qmlprofiler)
      ln -v  ${file} %{buildroot}%{_bindir}/${file}-qt5
      ln -sv ${file} ${file}-qt5
      ;;
    qml|qmlbundle|qmlmin|qmlscene)
      ln -v  ${file} %{buildroot}%{_bindir}/${file}
      ln -v  ${file} %{buildroot}%{_bindir}/${file}-qt5
      ln -sv ${file} ${file}-qt5
      ;;
    *)
      ln -v  ${file} %{buildroot}%{_bindir}/${file}
      ;;
  esac
done
popd

pushd %{buildroot}%{_qt5_libdir}
for file in libQt5*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${file}
  rm -fv "$(basename ${file} .prl).la"
  sed -i -e "/^QMAKE_PRL_LIBS/d" ${file}
done
popd


%check
%if 0%{?tests}
export LD_LIBRARY_PATH=%{buildroot}%{_qt5_libdir}
export CTEST_OUTPUT_ON_FAILURE=1 PATH=%{buildroot}%{_qt5_bindir}:$PATH
make sub-tests-all %{?_smp_mflags}
xvfb-run -a dbus-launch --exit-with-session time \
make check -k -C tests ||:
%endif

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license LICENSE.LGPL*
%{_qt5_libdir}/libQt5Qml.so.5*
%{_qt5_libdir}/libQt5Quick*.so.5*
%{_qt5_plugindir}/qmltooling/
%{_qt5_archdatadir}/qml/

%files devel
%{_bindir}/qml*
%{_qt5_bindir}/qml*
%{_qt5_headerdir}/Qt*/
%{_qt5_libdir}/pkgconfig/Qt5*.pc
%{_qt5_libdir}/libQt5Qml*.{a,so,prl}
%{_qt5_libdir}/libQt5Quick*.{so,prl}
%{_qt5_libdir}/cmake/Qt5*/Qt5*Config*.cmake
%{_qt5_libdir}/libQt5PacketProtocol.{a,prl}
%{_qt5_libdir}/cmake/Qt5Qml/Qt5Qml_*Factory.cmake
%{_qt5_archdatadir}/mkspecs/{modules/*.pri,features/*.prf}
%dir %{_qt5_libdir}/cmake/{Qt5Qml/,Qt5Quick*/}
%{_qt5_examplesdir}/


%changelog
* Tue Sep 15 2020 liuweibo <liuweibo10@huawei.com> - 5.11.1-6
- Fix Source0

* Sat Feb 22 2020 yanzhihua <yanzhihua4@huawei.com> - 5.11.1-5
- modify python buildrequire

* Thu Nov 07 2019 yanzhihua <yanzhihua4@huawei.com> - 5.11.1-4
- Package init

