# The Fingerprint Generator

This fingerprint generator is based on a piece of work
created by William Westwood, called [Do You Exist](https://github.com/iwouldntbother/DoYouExist). 
I've had to reverse engineer the tensorflow requirements, as there have been some major changes, although it preserves
his original GAN work. I've simply packaged the generator in a docker container
so that it can be run separately from the rest of the systems on an older version of Python.

To create the docker container to run this section of code, simply run:
    
    zsh 
    docker build -t fingerprint-generator .
    docker run --name fingerprint-generator -p 4999:4999 fingerprint-generator

This will create a docker image called fingerprint-generator, and run it in a container called "fingerprint-generator".
The container maps port 4999 onto port 4999 of the host machine, and runs the system through a flask server. Each time
the "/fingerprint_gen_api" endpoint is hit, the system will generate a new fingerprint and return it as a json object.

Working backwards from the "clientTestSystem" function, it is possible to rebuild the image from the json object,
and as such it's very easy to continuously generate new fingerprints, whilst keeping this subsystem wholly separate from
the rest of the codebase.