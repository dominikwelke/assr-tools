# assr-tools

This package allows you to easily create and use frequency tagged auditory stimuli in PsychPy. 
It supports a (growing) number of stimuli: 
- different carrier waves, or upload of already existing wav-files you created with some other tools
- deliberate choice of modulation frequency (based on stimulus envelope). 

It further includes a hearing-threshold task to adapt the stimulus loudness for each individual participant.

**install within a virtual environment using pip:**
1. download repository files
2. open terminal and run `pip install -e .` within the unpacked folder

*!!make sure to pip install into an environment with working psychopy, otherwise problems might arise!!*

**use with psychopy standalone version:**
1. download repository files
2. copy the module file `assr-tools.py` to the folder with your own presentation script
3. import relevant modules using `import assr-tools` or `from assr_tools import AudiThreshold`

