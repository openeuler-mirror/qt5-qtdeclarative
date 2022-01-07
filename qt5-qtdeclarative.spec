%global __provides_exclude_from ^%{_qt5_archdatadir}/qml/.*\\.so$

Name:             qt5-qtdeclarative
Version:          5.15.2
Release:          2
License:          LGPLv2 with exceptions or GPLv3 with exceptions
Summary:          Qt5 module for declarative framework
Url:              http://www.qt.io
%global majmin %(echo %{version} | cut -d. -f1-2)
Source0:          https://download.qt.io/official_releases/qt/%{majmin}/%{version}/submodules/qtdeclarative-everywhere-src-%{version}.tar.xz
Source1:          qv4global_p-multilib.h

Patch1:           0005-QQuickView-docs-show-correct-usage-of-setInitialProp.patch
Patch2:           0006-QQuickWindow-Check-if-QQuickItem-was-not-deleted.patch
Patch3:           0007-Avoid-GHS-linker-to-optimize-away-QML-type-registrat.patch
Patch4:           0008-QML-Text-doesn-t-reset-lineCount-when-text-is-empty.patch
Patch5:           0009-Doc-mention-that-INCLUDEPATH-must-be-set-in-some-cas.patch
Patch6:           0010-qmlfunctions.qdoc-Add-clarification-to-QML_FOREIGN.patch
Patch7:           0011-Fix-QML-property-cache-leaks-of-delegate-items.patch
Patch8:           0012-QQuickTextInput-Store-mask-data-in-std-unique_ptr.patch
Patch9:           0013-Fix-crash-when-calling-hasOwnProperty-on-proxy-objec.patch
Patch10:          0014-Accessibility-event-is-sent-on-item-s-geometry-chang.patch
Patch11:          0015-qmltypes.prf-Take-abi-into-account-for-_metatypes.js.patch
Patch12:          0016-qv4qmlcontext-Fix-bounded-signal-expressions-when-de.patch
Patch13:          0017-Use-load-qt_tool-for-qmltime.patch
Patch14:          0018-qqmlistmodel-Fix-crash-when-modelCache-is-null.patch
Patch15:          0019-Show-a-tableview-even-if-the-syncView-has-an-empty-m.patch
Patch16:          0020-DesignerSupport-Don-t-skip-already-inspected-objects.patch
Patch17:          0021-QML-Fix-proxy-iteration.patch
Patch18:          0022-Fix-IC-properties-in-same-file.patch
Patch19:          0023-JIT-When-making-memory-writable-include-the-exceptio.patch
Patch20:          0024-doc-explain-QQItem-event-delivery-handlers-setAccept.patch
Patch21:          0025-Give-a-warning-when-StyledText-encounters-a-non-supp.patch
Patch22:          0026-Add-missing-limits-include-to-fix-build-with-GCC-11.patch
Patch23:          0027-Document-that-StyledText-also-supports-nbsp-and-quot.patch
Patch24:          0028-Support-apos-in-styled-text.patch
Patch25:          %{name}-gcc11.patch
Patch26:          qtdeclarative-5.15.0-FixMaxXMaxYExtent.patch


Obsoletes:        qt5-qtjsbackend < 5.2.0 qt5-qtdeclarative-render2d < 5.7.1-10
BuildRequires:    make 
BuildRequires:    gcc-c++ qt5-rpm-macros >= %{version} qt5-qtbase-devel >= %{version}
BuildRequires:    qt5-qtbase-private-devel python%{python3_pkgversion}
%{?_qt5:Requires: %{_qt5} = %{_qt5_version}}

%if 0%{?tests}
BuildRequires:    dbus-x11 mesa-dri-drivers time xorg-x11-server-Xvfb
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
%autosetup -n qtdeclarative-everywhere-src-%{version} -p1

%build
#HACK so calls to "python" get what we want
ln -s %{__python3} python
export PATH=`pwd`:$PATH

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
%{_qt5_libdir}/libQt5QmlModels.so.5*
%{_qt5_libdir}/libQt5QmlWorkerScript.so.5*
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
%{_qt5_libdir}/metatypes/qt5*_metatypes.json
%{_qt5_libdir}/cmake/Qt5Qml/Qt5Qml_*Factory.cmake
%{_qt5_archdatadir}/mkspecs/{modules/*.pri,features/*.prf}
%{_qt5_libdir}/cmake/Qt5QmlImportScanner/
%dir %{_qt5_libdir}/cmake/{Qt5Qml/,Qt5Quick*/}
%{_qt5_examplesdir}/


%changelog
* Mon Jan 7 2022 peijiankang <peijiankang@kylinos.cn> - 5.15.2-2
- rm qt5-qtdeclarative-5.15.2-7.eln112.src.rpm

* Wed Oct 13 2021 peijiankang <peijiankang@kylinos.cn> - 5.15.2-1
- update to upstream version 5.15.2

* Tue Oct 27 2020 wangxiao <wangxiao65@huawei.com> - 5.11.1-7
- delete python2 buildrequires

* Mon Sep 14 2020  liuweibo <liuweibo10@huawei.com> - 5.11.1-6
- Fix Source0

* Sat Feb 22 2020 yanzhihua <yanzhihua4@huawei.com> - 5.11.1-5
- modify python buildrequire

* Thu Nov 07 2019 yanzhihua <yanzhihua4@huawei.com> - 5.11.1-4
- Package init

