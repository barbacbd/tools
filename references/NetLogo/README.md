# Building NetLogo

This document will contain the information that I utilized during the src building of NetLogo on the following linux operating systems:

- Fedora


## Packages

- curl
- git
- java
  - java-1.8.0-openjdk.x86_64
  - java-1.8.0-openjdk-devel.x86_64
  - java-1.8.0-openjdk-headless.x86_64
  - java-1.8.0-openjdk-openjfx.x86_64
  - java-1.8.0-openjdk-openjfx-devel.x86_64
- pandoc
- nodejs

**Note**: _The devel versions may not be required, but were installed just in case_.

## Java

Install Java as noted in the [NetLogo documentation](https://github.com/NetLogo/NetLogo/wiki/Building).

The system was configured with Java 11 as the default, but this will **note** work for the source build of NetLogo.

Execute `update-alternatives --config java` to list the java versions and switch to the correct version.

```bash
[@fedora34-eve NetLogo]$ update-alternatives --config java

There are 2 programs which provide 'java'.

  Selection    Command
-----------------------------------------------
*  1           java-11-openjdk.x86_64 (/usr/lib/jvm/java-11-openjdk-11.0.15.0.10-1.fc34.x86_64/bin/java)
 + 2           java-1.8.0-openjdk.x86_64 (/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.332.b09-1.fc34.x86_64/jre/bin/java)
```

In the example output above, `#2` was selected to ensure that the java 1.8 code was selected.

### Set JAVA_HOME

`JAVA_HOME` is empty by default and it must be set. Following the example above, set JAVA_HOME to 

```bash
/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.332.b09-1.fc34.x86_64
```

We did **not** select the `jre` folder and we did **not** include the `bin` as JAVA will find that itself.

You should check that there are entries for `javafx` in both of the following locations:
- $JAVA_HOME/lib
- $JAVA_HOME/jre/lib

If these do **not** exist, then you need to make sure that `java-1.8.0-openjdk-openjfx.x86_64` is installed.


**Note**: Add $JAVA_HOME to your bashrc file.

```bash
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.332.b09-1.fc34.x86_64
```

