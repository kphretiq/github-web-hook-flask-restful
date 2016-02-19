#!/bin/bash

function STDERR () {
	/bin/cat - 1>&2
}
echo "Fake Payload error!" | STDERR
exit 1;
