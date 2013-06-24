scanalea
========

Project Description:
~~~~~~~~~~~~~~~~~~~
ScanAlea is a project of the collabration between HRPPC PlantScan project and INRIA VirtualPlants project on plant phenotyping.

A transition layer software between PlantScan software and OpenAlea plateform will be produced in ScanAlea project to 
allow transferring real plant 3D reconstruction data to OpenAlea platform and back forth, using only a modified mesh 
file as medium.

Requirement:
~~~~~~~~~~~~
You have to install:
    - OpenAlea
    - mayavi2

Usage:
~~~~~~~~~~

    - `Segmentation to MTG <http://nbviewer.ipython.org/urls/raw.github.com/pradal/scanalea/master/example/ScanAlea.ipynb>`_
    - `Light interception <http://nbviewer.ipython.org/urls/raw.github.com/pradal/scanalea/master/example/ScanAlea-Dataflow.ipynb>`_

Reference:
~~~~~~~~~~


Hacker guide
~~~~~~~~~~~~~

For young git user, here is a list of usefull commands:

Commit your modifications on YOUR local branch::
    
    git commit -am 'FIX - my message'

To publish your modifications on your github (like svn commit)::
    
    git push

To retrieve the modifications from others (svn update)::
    
    git pull

Finally to publish the patches on openalea/scanalea:
    Ask for a pull request






