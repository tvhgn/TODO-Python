#! /bin/bash

# Print message
echo Creating Ollama model from Modelfile...

# Create model
ollama create Henk -f ./Modelfile

# Print message if completed
echo Henk was created!
