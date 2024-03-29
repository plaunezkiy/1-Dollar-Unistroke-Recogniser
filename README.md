# 1-Dollar-Unistroke-Recogniser
The $1 Unistroke Recognizer implementation in Python with a GUI wrapper made in Kivy

The $1 Unistroke Recognizer is a 2-D single-stroke recognizer designed for rapid prototyping of gesture-based user interfaces. In machine learning terms, $1 is an instance-based nearest-neighbor classifier with a 2-D Euclidean distance function, i.e., a geometric template matcher. 

[*link to the original paper*](http://depts.washington.edu/acelab/proj/dollar/index.html) 

## Set up instructions:
* (optional) Set up the environment - venv:
     
     ```
     python -m venv venv
     source venv/bin/activate
     ```
* Install dependencies:
    * Kivy, numpu
         ```
         pip install kivy numpy
         ```
* Clone the repo on your machine
     ```
     git clone https://github.com/plaunezkiy/1-Dollar-Unistroke-Recogniser.git
     ```
* cd to the folder and fire it up
     ```
     cd 1-Dollar-Unistroke-Recogniser && python main.py
     ```
