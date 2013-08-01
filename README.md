wwatcher
==============

**wwatcher is a command line tool to monitor and analyze animal weights entered in Google Sheets**

##Requirements

* Python 2.7
* gspread
* matplotlib/pylab

##Basic Usage

###Check weights
```sh
python wwatcher.py username@coxlab.org animalName1 animalName2 animalName3 -c
```

This will make sure the last 4 weekday weights are above 90% of each animal's max weight. You may specify as many animals as you like, as well as an additional -d option to change the number of weekday weights you check. For example, -d 7 would check the last 7 weekday weights instead of 4.

###Graph weights
```sh
python wwatcher.py username@coxlab.org animalName1 animalName2 animalName3 -g
```

This will plot the user-specified animal weights over time, each on a separate graph.

###Graph all weights
```sh
python wwatcher.py username@coxlab.org animalName1 animalName2 animalName3 -a
```

This will splot the user-specified animal weights over time, all on the same graph.

###Regression
```sh
python wwatcher.py username@coxlab.org animalName1 animalName2 animalName3 -r
```

This will make a scatter plot with the x axis as max weights and the y axis as an average of the previous 4 weekday weights for each user-specified animal. It will also make a line of best fit.
