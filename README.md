# Team tournament seating generation

Designed for games with 4 players in a match and 4 players in a team, e.g. mahjong.

## How to run it

`python team_seating.py -t 20`

`-t` - number of teams

## Initial data

Initial data was taken from http://golfsoftware.com/tools/schedule/playall.html

## How does it work

The whole team seating generation works in 3 main stages.

On the first stage, we take initial seating (for individual tournament) and remove internal intersections within team, i.e. prevent players from one team to play one another. After this stage, seating is already suited for being used in online tournament, but is still poorly balanced.

On the second stage, we balance team intersections, i.e. make each pair of teams play approximately even number of games.

On the third stage, we balance players intersections, i.e. make each pair of players play approximately even number of games.
