#!/bin/bash

# check if we need to install npm
export npme=`which npm`
if [[ "$npme" != "" ]]; then
  cd "flaskr/static"
  if [[ -d "node_modules" ]]; then
    echo "No need to install node"
  else
      echo "Installing node!"
      npm install
  fi
  if [[ -d "dist" ]]; then
    echo "No need to build"
  else
      echo "Building!"
      npm run build
  fi
  cd ../../
else
  echo "Please install npm first."
fi

export FLASK_APP="flaskr"
flask run