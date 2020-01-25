#-----------------------------------------------------
# Mimas: conference submission and review system
# (c) Allan Kelly 2016-2020 http://www.allankelly.net
# Licensed under MIT License, see LICENSE file
# -----------------------------------------------------

# Written so we can remove numpy from dependencies

def mean(numbers):
    total = sum(numbers)
    return round(total / float(len(numbers)),2)

def average_middle(sorted_numbers, count):
    return (sorted_numbers[count/2]+sorted_numbers[(count/2)-1])/float(2)

def median(numbers):
    sorted_numbers = sorted(numbers)
    count = len(numbers)
    if (count % 2) == 1:
        return sorted_numbers[count/2] # zero based list so rounding down is good
    else:
        return average_middle(sorted_numbers, count)

