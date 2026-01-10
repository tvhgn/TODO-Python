#! /bin/bash

# Print message
echo \nCreating Ollama model from Modelfile...

# Create model
ollama create Henk -f ./Modelfile

# Print message if completed
echo \nHenk was created!
