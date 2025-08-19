#!/bin/bash

port="6384"
key="user_scene_*"

./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ keys user_scene_* | xargs ./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ del
./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ keys detectInfo_* | xargs ./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ del
./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ keys scenemap_* | xargs ./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ del
./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ keys gather_* | xargs ./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ del
./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ keys begather_* | xargs ./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ del


./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ keys se_* | xargs ./redis-cli -p ${port} -a Ax++[D.#zFrDjgKQ del

