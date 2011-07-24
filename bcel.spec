# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

#For fedora, we want a native gcj compilation
%define _with_gcj_support 1
#Fedora currently does not support maven
%define _without_maven 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

Name:           bcel
Version:        5.2
Release:        7.2%{?dist}
Epoch:          0
Summary:        Byte Code Engineering Library
License:        ASL 2.0
Source0:        %{name}-%{version}-src.tar.gz
#svn export https://svn.apache.org/repos/asf/jakarta/bcel/tags/BCEL_5_2
#tar czvf bcel-5.2-src.tar.gz BCEL_5_2
Source1:        pom-maven2jpp-depcat.xsl
Source2:        pom-maven2jpp-newdepmap.xsl
Source3:        pom-maven2jpp-mapdeps.xsl
Source4:        %{name}-%{version}-jpp-depmap.xml
#Source5:        commons-build.tar.gz
Source5:        bcel-jakarta-site2.tar.gz
Source6:        %{name}-%{version}-build.xml
Source7:        %{name}-%{version}.pom

Patch0:         %{name}-%{version}-project_properties.patch
URL:            http://jakarta.apache.org/%{name}/
Group:          Development/Libraries/Java
Requires:       regexp
BuildRequires:  ant
%if %{with_maven}
BuildRequires:  maven >= 0:1.1
BuildRequires:  saxon
BuildRequires:  saxon-scripts
BuildRequires:  maven-plugins-base
BuildRequires:  maven-plugin-changelog
BuildRequires:  maven-plugin-changes
BuildRequires:  maven-plugin-developer-activity
BuildRequires:  maven-plugin-jxr
BuildRequires:  maven-plugin-license
BuildRequires:  maven-plugin-pmd
BuildRequires:  maven-plugin-test
BuildRequires:  maven-plugin-xdoc
Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2
%else
BuildRequires:  jdom
BuildRequires:  velocity
BuildRequires:  jakarta-commons-collections
#excalibur-avalong-logkit should be used once Maven is supported in Fedora
BuildRequires: avalon-logkit
#BuildRequires:  excalibur-avalon-logkit
BuildRequires:  werken-xpath
#BuildRequires:  ant-apache-regexp
%endif
BuildRequires:  regexp
BuildRequires:  jpackage-utils >= 0:1.7.2
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
Requires(post):   java-gcj-compat
Requires(postun): java-gcj-compat
%endif

%description
The Byte Code Engineering Library (formerly known as JavaClass) is
intended to give users a convenient possibility to analyze, create, and
manipulate (binary) Java class files (those ending with .class). Classes
are represented by objects which contain all the symbolic information of
the given class: methods, fields and byte code instructions, in
particular.  Such objects can be read from an existing file, be
transformed by a program (e.g. a class loader at run-time) and dumped to
a file again. An even more interesting application is the creation of
classes from scratch at run-time. The Byte Code Engineering Library
(BCEL) may be also useful if you want to learn about the Java Virtual
Machine (JVM) and the format of Java .class files.  BCEL is already
being used successfully in several projects such as compilers,
optimizers, obsfuscators and analysis tools, the most popular probably
being the Xalan XSLT processor at Apache.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Documentation

%description javadoc
%{summary}.

%package manual
Summary:        Manual for %{name}
Group:          Development/Libraries/Java

%description manual
%{summary}.

%prep
#cat <<EOT
#
#                If you dont want to build with maven,
#                give rpmbuild option '--without maven'
#
#EOT

%setup -q -n BCEL_5_2
gzip -dc %{SOURCE5} | tar xf -
# remove all binary libs
#find . -name "*.jar" -exec rm -f {} \;
for j in $(find . -name "*.jar"); do
    %{__mv} $j ${j}.no
done
%if %{without_maven}
mkdir jakarta-site2/lib
pushd jakarta-site2/lib/
  build-jar-repository -s -p . jdom
  build-jar-repository -s -p . velocity
  build-jar-repository -s -p . commons-collections
  build-jar-repository -s -p . avalon-logkit
  build-jar-repository -s -p . werken-xpath
popd
%endif
cp %{SOURCE6} build.xml
%patch0 -b .sav

# fix wrong-file-end-of-line-encoding
sed -i 's/\r//' docs/verifier/V_API_SD.eps docs/eps/classloader.fig

%build
%if %{with_maven}
export DEPCAT="$(pwd)/%{name}-%{version}-depcat.new.xml"
echo '<?xml version="1.0" standalone="yes"?>' > $DEPCAT
echo '<depset>' >> $DEPCAT
for p in $(find . -name project.xml); do
    pushd $(dirname $p)
        /usr/bin/saxon project.xml %{SOURCE1} >> $DEPCAT
    popd
done
echo >> $DEPCAT
echo '</depset>' >> $DEPCAT
/usr/bin/saxon $DEPCAT %{SOURCE2} > %{name}-%{version}-depmap.new.xml

for p in $(find . -name project.xml); do
    pushd $(dirname $p)
        %{__cp} -pr project.xml project.xml.orig
        /usr/bin/saxon -o project.xml project.xml.orig %{SOURCE3} \
            map="%{SOURCE4}"
    popd
done

export MAVEN_HOME_LOCAL="$(pwd)/.maven"

maven -e \
        -Dmaven.repo.remote=file:/usr/share/maven/repository \
        -Dmaven.home.local=${MAVEN_HOME_LOCAL} \
        jar:jar javadoc:generate xdoc:transform
%else
#ant -Dregexp.jar="file://$(build-classpath regexp)" jar javadoc
ant     -Dbuild.dest=build/classes -Dbuild.dir=build -Ddocs.dest=docs \
        -Ddocs.src=xdocs -Djakarta.site2=jakarta-site2 -Djdom.jar=jdom.jar \
        -Dregexp.jar="file://$(build-classpath regexp)" \
        jar javadoc xdocs
%endif

%install
%{__rm} -rf %{buildroot}
# jars
%{__mkdir_p} %{buildroot}%{_javadir}
%{__install} -m 0644 target/%{name}-%{version}.jar \
    %{buildroot}%{_javadir}/%{name}-%{version}.jar
(
    cd %{buildroot}%{_javadir}
    for jar in *-%{version}*; do 
        %{__ln_s} ${jar} `echo $jar | %{__sed}  "s|-%{version}||g"`
    done
)
# depmap frags
%add_to_maven_depmap %{name} %{name} %{version} JPP %{name}
%add_to_maven_depmap org.apache.bcel %{name} %{version} JPP %{name}
# pom
%{__mkdir_p} %{buildroot}%{_datadir}/maven2/poms
%{__install} -m 0644 %{SOURCE7} \
    %{buildroot}%{_datadir}/maven2/poms/JPP-%{name}.pom

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%if %{with_maven}
%{__cp} -pr target/docs/apidocs/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__rm} -rf target/docs/apidocs
%else
%{__cp} -pr dist/docs/api/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__rm} -rf dist/docs/api
%endif
%{__ln_s} %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

# manual
%{__mkdir_p} %{buildroot}%{_docdir}/%{name}-%{version}
%if %{with_maven}
%{__cp} -pr target/docs/* %{buildroot}%{_docdir}/%{name}-%{version}
%else
%{__cp} -pr docs/* %{buildroot}%{_docdir}/%{name}-%{version}
%endif
%{__cp} LICENSE.txt %{buildroot}%{_docdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
%{__rm} -rf %{buildroot}

%post
%update_maven_depmap
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]; then
    %{_bindir}/rebuild-gcj-db
fi
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]; then
    %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}
%doc %{_docdir}/%{name}-%{version}/LICENSE.txt 
%{_javadir}/*
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-*.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%files manual
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}

%changelog
* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0:5.2-7.2
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:5.2-7.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:5.2-6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Dec 04 2008 Permaine Cheung <pcheung at redhat.com> 0:5.2-5.1
- Do not install poms in /usr/share/maven2/default_poms

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:5.2-5
- drop repotag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:5.2-4jpp.2
- Autorebuild for GCC 4.3

* Tue Jan 22 2008 Permaine Cheung <pcheung at redhat.com> 0:5.2-3jpp.1
- Merge with upstream

* Mon Jan 07 2008 Permaine Cheung <pcheung at redhat.com> 0:5.2-2jpp.2
- Fixed unowned directory (Bugzilla 246185)

* Fri Nov 16 2007 Ralph Apel <r.apel@r-apel.de> 0:5.2-3jpp
- Install poms unconditionally
- Add pom in ./maven2/default_poms
- Add org.apache.bcel:bcel depmap frag

* Wed Sep 19 2007 Permaine Cheung <pcheung at redhat.com> 0:5.2-2jpp.1
- Update to 5.2 in Fedora

* Mon Sep  4 2007 Jason Corley <jason.corley@gmail.com> 0:5.2-2jpp
- use official 5.2 release tarballs and location
- change vendor and distribution to macros
- add missing requires on and maven-plugin-test, maven-plugins-base, and
  maven-plugin-xdoc 
- macro bracket fixes
- remove demo subpackage (examples are not included in the distribution tarball)
- build in mock

* Wed Jun 27 2007 Ralph Apel <r.apel@r-apel.de> 0:5.2-1jpp
- Upgrade to 5.2
- Drop bootstrap option: not necessary any more
- Add pom and depmap frags

* Fri Feb 09 2007 Ralph Apel <r.apel@r-apel.de> 0:5.1-10jpp
- Fix empty-%%post and empty-%%postun
- Fix no-cleaning-of-buildroot

* Fri Feb 09 2007 Ralph Apel <r.apel@r-apel.de> 0:5.1-9jpp
- Optionally build without maven
- Add bootstrap option

* Thu Aug 10 2006 Matt Wringe <mwringe at redhat.com> 0:5.1-8jpp
- Add missing requires for Javadoc task

* Sun Jul 23 2006 Matt Wringe <mwringe at redhat.com> 0:5.1-7jpp
- Add conditional native compilation
- Change spec file encoding from ISO-8859-1 to UTF-8
- Add missing BR werken.xpath and ant-apache-regexp

* Tue Apr 11 2006 Ralph Apel <r.apel@r-apel.de> 0:5.1-6jpp
- First JPP-1.7 release
- Use tidyed sources from svn
- Add resources to build the manual
- Add examples to -demo subpackage
- Build with maven by default
- Add option to build with straight ant

* Fri Nov 19 2004 David Walluck <david@jpackage.org> 0:5.1-5jpp
- rebuild to fix packager

* Sat Nov 06 2004 David Walluck <david@jpackage.org> 0:5.1-4jpp
- rebuild with javac 1.4.2

* Sat Oct 16 2004 David Walluck <david@jpackage.org> 0:5.1-3jpp
- rebuild for JPackage 1.6

* Fri Aug 20 2004 Ralph Apel <r.apel at r-apel.de> 0:5.1-2jpp
- Build with ant-1.6.2

* Sun May 11 2003 David Walluck <david@anti-microsoft.org> 0:5.1-1jpp
- 5.1
- update for JPackage 1.5

* Mon Mar 24 2003 Nicolas Mailhot <Nicolas.Mailhot (at) JPackage.org> - 5.0-6jpp
- For jpackage-utils 1.5

* Tue Feb 25 2003 Ville Skyttä <ville.skytta at iki.fi> - 5.0-5jpp
- Rebuild to get docdir right on modern distros.
- Fix License tag and source file perms.
- Built with IBM's 1.3.1SR3 (doesn't build with Sun's 1.4.1_01).

* Tue Jun 11 2002 Henri Gomez <hgomez@slib.fr> 5.0-4jpp
- use sed instead of bash 2.x extension in link area to make spec compatible
  with distro using bash 1.1x

* Tue May 07 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 5.0-3jpp 
- vendor, distribution, group tags

* Wed Jan 23 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 5.0-2jpp 
- section macro
- no dependencies for manual and javadoc package

* Tue Jan 22 2002 Henri Gomez <hgomez@slib.fr> 5.0-1jpp
- bcel is now a jakarta apache project
- dependency on jakarta-regexp instead of gnu.regexp 
- created manual package

* Sat Dec 8 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.4.1-2jpp
- javadoc into javadoc package
- Requires: and BuildRequires: gnu.regexp

* Wed Nov 21 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 4.4.1-1jpp
- removed packager tag
- new jpp extension
- 4.4.1

* Thu Oct 11 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.4.0-2jpp
- first unified release
- used lower case for name
- used original tarball
- s/jPackage/JPackage

* Mon Aug 27 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 4.4.0-1mdk
- first Mandrake release
