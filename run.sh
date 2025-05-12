#!/bin/bash

# 컨테이너 빌드 및 실행
docker-compose down --remove-orphans
docker-compose build
docker-compose up -d

# 상태 확인
docker-compose ps