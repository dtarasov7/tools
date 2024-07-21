#!/bin/bash

set -x

#Create employess data object
declare -A employees_data


employees_data[status]="success"
employees_data[message]="Employee list"
employees_data[start]=0
employees_data[total_results]=1

#Create data element Object
declare -A data_elem_obj


data_elem_obj[empId]=123
data_elem_obj[name]="Tim"
data_elem_obj[designation]="Engineer"


employees_data[data]=${data_elem_obj[@]}


echo ${employees_data[data][name]}

echo ${data_elem_obj[@]}
#output: Tim 123 Engineer

echo ${data_elem_obj[name]}

echo ${employees_data[@]}
#output: 0 success 1 Tim 123 Engineer Employee list
