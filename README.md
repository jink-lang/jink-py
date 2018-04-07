# jink

> Jink is a strongly-typed, JavaScript-like programming language.

[![Build Status](https://travis-ci.org/Jacob-Noah/jink.svg?branch=master)](https://travis-ci.org/Jacob-Noah/jink)

I made Jink to prove to myself that I could, and I plan to support it as long as I see fit. It has been my most difficult project, which makes it the most fun!

## Example

```jink
int example_func(int in) {
    return ++in
}

int out = example_func(1336)
print(out) :: Prints 1337 to the console
```

## Prerequisites

* Python 3.6+

## Contributing

I will set up a contribution guide when I can. In the meantime, feel free to provide feedback any way you see fit. This project is still fairly new, after all.

## Acknowledgements

* Enormous thanks to [king1600](https://github.com/king1600) for helping me to better understand interpreter design and providing me the resources and support I needed to carry out this project.

* This project also would not have been possible without the incredible resources on implementing a programming language at [Mihai Bazon's blog](http://lisperator.net).

## License

This project is distributed under the MIT License - see the [license file](LICENSE) for details.

Copyright © 2018+ Jacob Buzalski

## P.S.

Don't call me silly for making an interpreted language strongly-typed, call me silly for making it with a loosely-typed language. Haha! xoxo