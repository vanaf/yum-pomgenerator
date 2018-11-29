# yum-pomgenerator
Plugin for yum that converts rpm dependencies to maven ones, to upload them into maven repo.

```
[van@iafonichev-nb yum-pomgenerator]$ podman build -t yum-pomgenerator .
[van@iafonichev-nb yum-pomgenerator]$ podman run -e YUM_PACKAGES=podman -e MVN_REPO_ID=some-nexus -e MVN_REPO_URL=some://nexus/url -v /tmp/rpms:/var/rpm-poms:Z yum-pomgenerator
```

This will produce 
```
==== MVN DEPLOY COMMANDS ====
mvn deploy:deploy-file commands to be executed
...
==== END OF MVN DEPLOY COMMANDS ====
```

Now feel free to execute them:
```
[van@iafonichev-nb yum-pomgenerator]$ cd /tmp/rpms/
[van@iafonichev-nb yum-pomgenerator]$ mvn deploy:deploy-file commands to be executed

```

Currently works only with packages in repos. TODO: 
* Support non-repo, provided rpm-packages
* Support adding additional repos before install
