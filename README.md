# YouTube Manager

### Prerequisites

- python 3.8
- make
- nodeJS
- yarn

<details><summary>Install prerequisites (click to show details)</summary>
<p>

**Windows**
- Install `python` 3.8 from Microsoft Store  
https://www.microsoft.com/en-us/p/python-38/9mssztt1n39l
- Install `Chocolatey` (Windows package manager)  
https://chocolatey.org/courses/installation/installing?method=installing-chocolatey?quiz=true#cmd)
- Open `powershell.exe` as admin
- Install `make` with Chocolatey
    ```
    choco install make
    ```
- Install `yarn` with Chocolatey  
(`nodeJS` will be installed as it is required by `yarn`)
    ```
    choco install yarn
    ```
</p>
</details>

### Installation

```bash
make install
```

### Upload

```bash
make uiupload
```
Then choose to which destination channel to upload

### Configuration
- See <a href="./settings.py">`settings.py`</a>


### (Re)generate `requirements.txt` when new python dependencies are added 

1. Requirement: `pipreqs` installed
```bash
pip install pipreqs
```
2. Run `pipreqs` in your current project root folder
```bash
pipreqs . --force
```

### Recommended code editor
- Visual Studio Code


#### Other

- How to use Path
https://medium.com/@ageitgey/python-3-quick-tip-the-easy-way-to-deal-with-file-paths-on-windows-mac-and-linux-11a072b58d5f