#!/bin/bash
set -e
psql -U assay -d postgres -c "CREATE DATABASE assay_test OWNER assay;"
