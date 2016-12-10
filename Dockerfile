FROM percona/percona-xtradb-cluster:latest

COPY ["$PWD/config/my.cnf", "/etc/my.cnf"]
RUN apt-get update -y && apt-get install -y vim less

CMD ["/entrypoint.sh"]
ENTRYPOINT ["bash", "-x", "/entrypoint.sh"]
