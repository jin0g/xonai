#!/usr/bin/env xonsh
# Simple test to see natural language queries working

# Load xoncc xontrib
xontrib load xoncc

print("=== Testing natural language query ===")
print("Query: 'list current directory files'\n")

# Execute the query
list current directory files

print("\n=== Query completed ===")