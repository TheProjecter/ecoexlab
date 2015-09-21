**EcoExLab Prototype** - A software for economic experiments and simulations

(c) 2012 by Eckhart Arnold

License: GPLv3  (see LICENSE.TXT)


# Purpose #

EcoExLab is the attempt to create an easy to use and easy to adapt
software for conducting laboratory experiments and simulations in
economics or other social sciences with up to date technology.

One of the goals is to connect simulation research with experimental
research by both on the same models and software systems. An
experiment will then just be an agent-based simulation where the
software agents are replaced by real humans in front of a computer
screen (or in front of their iPad). And an agent-based simulation will
just be an experiment where all or some human agents are replaced by
bots (i.e. computer agents).

If this works as intended, then it will solve two problems at the same
time: 1) Agent based simulations will very easily be validated
empirically. 2) Reproduction of experimentally observed results with
computer agents (bots) will allow generating explanatory hypotheses
for the observed behavior.

The long-term goal is to provide a complete framework for experimental
economics somewhat like the aging z-tree system
http://www.iew.uzh.ch/ztree/index.php .

The short term goal is to start off with prototyping a particular
experiment to gain experience about how to best structure the software
and which technologies to use, before embarking on the development of
a general framework.


# Current State #

EcoExLab will consist of four components:

1) an engine or "backend"
2) a report tool for evaluating and presenting experimental data
3) a user interface or "frontend" for the participants of the experiment
4) a server for connecting the backend with the frontends over a network

Presently, there exits a prototype that re-enacts a particular economic
experiment [1](1.md) as a computer simulation.  It consists of a simulation engine
and a (rudimentary) report tool.

In order to check out the prototpy run Test.py from the shell with the
command:

> python Test.py

When the simulation and report generation have finished, a browser window
should open that displays the results. Please note, that the computer
agents so far do not quite behave like humans. So, expect the results to
differ widely from those reported in the experimental study upon which
this simulation is modeled.

References:

Gürerk Özgür / Irlenbusch, Bernd / Rockenbach, Bettina: The Competitive Advantage of Sanctioning Insitutions. in: Science 312 (2006), p. 108–111.


# Requirements #

python 2.7 or above  (the engine should work with python 3.2 but report
> generation requires matplotlib which is not yet
> compatible with python 3.2)
matplotlib 1.0 or above
numpy 1.5      or above