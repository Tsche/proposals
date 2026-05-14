FROM ubuntu:latest
ARG USERNAME="root"


USER root
RUN apt-get update && apt-get install -y make sudo gawk

RUN getent passwd \
      | awk -F: '($3 >= 1000) && ($1 != "nobody") {print $1}' \
      | xargs -r -n 1 userdel -r

RUN if [ "${USERNAME}" != "root" ]; then \
      groupadd --gid 1000 "${USERNAME}" || true && \
      useradd -s /bin/bash -m -u 1000 -g 1000 "${USERNAME}" && \
      mkdir -p /etc/sudoers.d && \
      echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/"${USERNAME}" && \
      chmod 0440 /etc/sudoers.d/"${USERNAME}"; \
    fi

# Pandoc (markdown papers)
RUN apt-get install -y curl \
      python3 python3-pip texlive-xetex python3-venv python3-requests pandoc

# Cowel
RUN apt-get install -y nodejs npm 
RUN npm install --global cowel

USER ${USERNAME}
