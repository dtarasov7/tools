#FROM python:3.8-alpine3.13 as builder
FROM python:3.9.8-slim-buster as builder

# Add the community repo for access to patchelf binary package
#RUN echo 'https://dl-cdn.alpinelinux.org/alpine/v3.13/community/' >> /etc/apk/repositories
#RUN apk --no-cache upgrade && apk --no-cache add build-base tar musl-utils openssl-dev patchelf 
RUN apt-get update
RUN apt-get -y install patchelf git python3-wheel gcc
#cmake
# patchelf-wrapper is necessary now for cx_Freeze, but not for Curator itself.
RUN python3 -m pip install --upgrade pip
RUN pip3 install setuptools cmake wheel
RUN pip3 install --upgrade git+https://github.com/anthony-tuininga/cx_Freeze.git@main
#RUN pip3 install --upgrade cx_Freeze
RUN pip3 install patchelf-wrapper
# cmake

COPY . .
#RUN ln -s /lib/libc.musl-x86_64.so.1 ldd
RUN ln -s /lib /lib64
RUN pip3 install -r requirements.txt
RUN python3 setup.py build_exe

FROM debian:buster-slim
RUN apt-get update
RUN apt-get -y install libssl-dev
#RUN apk --no-cache upgrade && apk --no-cache add openssl-dev expat
COPY --from=builder build/exe.linux-x86_64-3.9 /curator/
RUN mkdir /.curator

#USER nobody:nobody
ENV LD_LIBRARY_PATH /curator/lib:$LD_LIBRARY_PATH
ENTRYPOINT ["/curator/curator"]

