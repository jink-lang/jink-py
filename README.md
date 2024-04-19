# Jink (Python Interpreter)

[![CircleCI](https://img.shields.io/circleci/build/github/jink-lang/jink-py?label=tests)](https://circleci.com/gh/jink-lang/jink-py/tree/master)
[![Discord](https://img.shields.io/discord/365599795886161941?label=Discord)](https://discord.gg/cWzcQz2)
![License](https://img.shields.io/github/license/jink-lang/jink-py)
![GitHub contributors](https://img.shields.io/github/contributors-anon/jink-lang/jink-py)
![GitHub Repo stars](https://img.shields.io/github/stars/jink-lang/jink-py?style=social)
---

> A simplistic Jink interpreter built using Python.

## Jink
This is the original implementation of the [Jink](https://github.com/jink-lang/jink) programming language. More information can be found at the new repo.

## Goal Checklist

(Not in or by any particular order or specification)

- [✓] Interpreter & REPL
- [ ] Classes & OOP
- [ ] Arrays
- [½] Modularity & packaging
- [ ] Filesystem read & write
- [ ] Networking

## Example

```js
fun add(let a, let b) {
    return a + b
}

let c = add(1000, 337)
print(c) // Print 1337 to the console!
```

For more examples, check the [examples](./examples) folder.

## Installation

Assuming you have Python 3.6 or newer, you can get started right away after cloning the project!

To launch the REPL:

```cmd
python jink.py
```

To execute your own files:

```cmd
python jink.py C:/path/to/file.jk
```

To execute the example files:

```cmd
python jink.py ./examples/01-hello_world.jk
```

### Building

#### Prerequisites

* Python 3.6+

#### Windows

1. Clone the project.
2. Run the included `build-executable.bat` file; this will install cx_Freeze and build the executable.

```cmd
cd build/exe.win32-3.x
jink.exe C:/path/to/your_file.jk
```

Optionally, you can move the contents of the /build/exe.win32-3.x folder to a folder you've added to your PATH. This will allow you to run Jink via your command line.

## Contributing

I will set up a contribution guide when I can. In the meantime, feel free to provide feedback in any way you see fit. If you do decide to submit a PR, make your decisions as clear as possible and provide as many details as you can.

## Acknowledgements

* Enormous thanks to [king1600](https://github.com/king1600) for helping me to better understand interpreter and compiler design and providing me the resources and support I needed to carry out this project.

* This project also would not have been possible without the incredible resources on PL implementation at [Mihai Bazon's blog](http://lisperator.net).

## License

This project is distributed under the MIT License - see the [license file](LICENSE) for details.

Copyright © 2018-2024 Jacob
