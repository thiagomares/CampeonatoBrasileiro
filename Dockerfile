FROM quay.io/astronomer/astro-runtime:12.4.0


USER root

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

ENV AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True

RUN sudo mkdir -p /usr/local/airflow/dados && chmod -R 777 /usr/local/airflow/dados


