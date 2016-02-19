#!/bin/bash

function STDERR () {
	cat - 1>&2
}
echo "Fake Payload error!" | STDERR
exit 1;
