#!/bin/bash

echo "$1" >&1
echo "$2" >&2
echo 'foo' >&1
echo 'bar' >&2
echo 'あいうえお' >&1
echo 'かきくけこ' >&2
echo $'\xff\xfe' >&1
echo $'\xfd\xfc' >&2
