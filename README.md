# Project for CS6675

## Spring 2022

Any usage of this project should appropriately reference this repository.

# Info

Scripts used to benchmark and perform other experiments can be found in the research directory

The implementation of the blockchain and the proof of concept web server can be found in the web_chain directory

## Running Proof of Concept

![ezgif-4-3ebaf297f3](https://user-images.githubusercontent.com/6844618/165016900-967ea174-aec7-4277-871e-7b530fe4ae90.gif)



Assuming all requirements have been installed

start web server

```shell
cd web_chain
uvicorn poc:app
```

run validation script

```shell
cd web_chain
./validate
```
