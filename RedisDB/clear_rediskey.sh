#!/bin/bash

port="6384"
key="detectInfo_*"

./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ keys ${key} | xargs ./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ del
