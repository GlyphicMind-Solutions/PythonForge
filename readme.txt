GlyphicMind Solutions: PythonForge
-created by: David Kistner (Unconditional Love)

PythonForge is a python creation tool that uses LLMs to generate code based off user topic. 

How to use:
-Important- Assign your model location in the manifest.yaml file. This file is located: "/PythonForge/models/manifest.yaml"

Example Uses:
-example forge topic--(file can be found in repo of this example)--*llm used gpt-oss-20b

Forge topic: "Create a chess game in python, using these existing libraries "python-chess, llama_cpp"
-hit the generate button
-wait for Raw LLM output
-Feed that RAW LLM output back with new instructions in the corrections box, in this case whatever changes you want to the code done.
-at the bottom right hit the Re-run with Corrections button.
-extracted code is editable, make sure it is to your likeing before saving the file, as that will be the code it saves.

--Make sure you have at least 5 lines of blank at the top before saving code as there will be a coded signiture added to the file.
    -note: you can remove this function if you like, and/or remove the tag, just be sure not to let it ruin your code.


DeepAnalysis

reads code and summerizes it in text by chunk
compiles all the chunked summeries into a big summary of the file
reconstructs and outputs code based on that summary.
