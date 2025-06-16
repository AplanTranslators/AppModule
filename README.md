# App-Module


This is an application module, it includes tools and basic structures for generating Aplan Files.

It provides tools such as:
    - TranlatorTool - A basic tool that performs translation of a specified file (SV or VHDL) depending on the provided translator.
    - Testing Tool - Generation testing tool, generates files and compares them with reference ones.
    - Regeneration Tool - File regeneration tool.

## TranlatorTool Base Preparation
```python
    if __name__ == "__main__":
        tool = BaseTool("ToolName") # Create Base tool object
        tool.setType("sv") # Set the testing file type
        tool.start("file_path","path to result") # if "path to result" not specified , tool create default "result" folder

```

## Testing Tool Preparation


Requires a json file with example data used for the test.

```json
[
        {
            "file": "examples/initial/initial.sv",
            "result_dir": "examples/initial/test_result",
            "aplan_dir": "examples/initial/aplan"
        }
]
```


```python
    if __name__ == "__main__":
        tool = BaseTool() # Create Base tool object
        tool.setType("sv") # Set the testing file type
        tool.tests_start("path to json file with examples data")
```


## Regeneration Tool  Preparation

For this tool you can have the same example file as for the Testing tool or run one specific example

```python
    if __name__ == "__main__":
        tool = BaseTool() # Create Base tool object
        tool.setType("sv") # Set the regeneration file type
        tool.regeneration_start(examples_list_path = "path to json file with examples data", )
```

```python
    if __name__ == "__main__":
        tool = BaseTool() # Create Base tool object
        tool.setType("sv") # Set the regeneration file type
        tool.regeneration_start(path_to_sv = "path to exampe file")
```