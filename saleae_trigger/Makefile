#
# This is a project Makefile. It is assumed the directory this Makefile resides in is a
# project subdirectory.
#

PROJECT_NAME := example

include $(IDF_PATH)/make/project.mk

cap-mon: $(call prereq_if_explicit,%flash)
	python3 ./capture.py
	${MAKE} monitor

