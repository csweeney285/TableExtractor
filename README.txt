#### READ ME

In order to run our software, please install all the necessary dependencies by running the following commands:

The script requires that homebrew be installed on the computer to install poppler. If you do not have homebrew installed then run the following command as a prerequisite:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

(cd into the working directory of the software)
sudo chmod a+x install_dependencies.sh
(Type in your password)
./install_dependencies.sh

Now you can run the software by calling:
python TableExtractor.py

A simple GUI will appear. The user will select a language to parse. The default is english. And then select a pdf to analyze. Our software will then run and print out the results. This is a convenient way to test updates.