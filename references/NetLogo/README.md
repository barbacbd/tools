# Building NetLogo

This document will contain the information that I utilized during the src building of NetLogo on the following linux operating systems:

- RedHat Enterprise Linux (Rhel) 8.x


# Java

Install Java as noted in the [NetLogo documentation](https://github.com/NetLogo/NetLogo/wiki/Building).

- java-1.8.0-openjdk.x86_64
- java-1.8.0-openjdk-devel.x86_64

**Note**: _I grabbed the devel version too just in case._

In your bash file, make sure that `JAVA_HOME` is set and added to your path. To find where your JAVA information is located, check

- `java -version`
- which java

You will find that java is located in `/usr/bin` but this is **only** a single alternative and more than likely just the `jre`. To find the other locations for the entire jdk run:

`alternatives --list`

This led to the discovery of the jdk path and ultimately setting the following in bashrc:

- `export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.282.b08-4.el8.x86_64`
- `export PATH=$JAVA_HOME:$PATH`

**Note**: _Do not add the extra `bin` in the JAVA_HOME as it will lead to path errors_.

# pandoc

```bash
wget https://github.com/jgm/pandoc/releases/tag/2.18/pandoc-2.18-linux-amd64.tar.gz;
tar -xvzf pandoc-2.18-linux-amd64.tar.gz;
cd pandoc-2.18;

# Move the executables from bin to /usr/bin
sudo mv bin/* /usr/bin;

# Move the man doc pages to /usr/share
sudo mv share/man/man1/* /usr/share/man/man1/;
```

**Note**: _The version of pandoc may change visit the [downloads](https://github.com/jgm/pandoc/releases) for more versions_.
