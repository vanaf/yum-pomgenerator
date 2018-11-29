FROM centos:7

COPY pomgenerator.py /usr/lib/yum-plugins/
COPY pomgenerator.conf /etc/yum/pluginconf.d/


ENV MVN_REPO_ID=remote-repository \
    MVN_REPO_URL=please://specify.mvn.url/by/setting/MVN_REPO_URL \
    POM_DIR=/var/rpm-poms

VOLUME /var/cache/yum /var/tmp $POM_DIR



CMD /bin/yum --generate-poms --downloadonly --downloaddir="${POM_DIR}" install $YUM_PACKAGES
