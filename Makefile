# Makefile for source rpm: dbus
# $Id$
NAME := dbus
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
