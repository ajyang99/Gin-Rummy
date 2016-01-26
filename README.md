# Gin-Rummy
A Sophisticated GUI Recreation of Classic Card Game Gin Rummy in Python with AI Player, Sorting, Brute-force Optimized Searching and Greedy Algorithms

You can play it live here: http://www.codeskulptor.org/#user41_UxE3vLfPO1_5.py

Rules: http://www.pagat.com/rummy/ginrummy.html

Rules Synopsis:
- Terms: 
- Each Card has a value: 'A' = 1, '2' = 2, ..., '10' = 'J' = 'Q' = 'K" = 10.
- A "meld" contains at least 3 cards of the same number, or at least 3 consecutive numbered cards of the same suit. For example, "Heart 3", 
"Heart 4", and "Heart 5" would make a meld, and "Heart 3", "Square 3", and "Diamond 3" would also make a meld.
- If a card is in a meld, then it doesn't count as a "deadwood". (However, every card can only be allowed in ONE meld: eg.
if you have "Heart 3", "Heart 4", "Heart 5", "Diamond 3", "Square 3" at the same time, then your deadwoods are either "Heart 4" and 
"Heart 5", or "Diamond 3" and "Square 3" - although every card can be arranged to be in a meld, since "Heart 3" can only be used once,
there are always two deadwoods.)
- Deadwood Value = value of all the deadwoods in the hand of one player

- In this game, each player has 10 cards. Each time each player first draws a card from either the stock or the discard pile, and then
discards a card of their choice. The goal of the game is to get the "deadwood" value as small as possible at the end of the game.

- When the "deadwood value" of one player is less than or equal to 10, he/she can choose to "knock" (i.e. end the game) (also you can choose not to). Then both playerswill show their cards. The player who didn't knock will "lay off" if possible, meaning, he/she can get rid of the deadwoods that will complement the melds of the knocker (e.g. if player A knocks and "Heart K", "Diamond K", and "Sqaure K" is one of A'smelds, and if player B happens to have "Club K" in his deadwoods, then "Club K" wouldn't count towards B's deadwoods value). Then both players will calculate their deadwood value after the "lay-off". Say if A knocked, and A's deadwood value is still less than B's deadwood value, then the difference between these two values will add to A's score; if B's deadwood value is less than or the same as A's value, then A has been "undercut", and not only the difference, but also a bonus 10 points, will be added to B's score.

- The game will be automatically over if one of the player's deadwood value is 0. Then the player "goes Gin", and the deadwood value
difference plus a 20 bonus will be added to the player's score. If after the layoff the other player goes Gin too, then he will also
get a 20 bonus.

- Then the next round will continue. The game will be over when one player scores more than 100 points.

How to Start: You first decide whether or not you want the faced-up card. If so, you take the card by single clicking on it, and then you should discard a card from your hand, by single clicking on the card you don't want, and then single clicking on the "discard pile", which is where the faced-up card was. If you don't want the card, hit the Decline button on the left and wait for the Computer Player's action.

How to Draw/Discard: Then you play the game, by drawing a card first from either the stock pile or the discard pile and then discarding a card from your hand. Thus you always have 10 cards in your hand. (Note that if you draw from the discard pile, you can't discard the card you just draw; but if you draw from the stock pile, you can discard the card you just draw immediately if you don't like it.)

How to Sort: There is a "sort" on the button that can do the sorting for you by putting the "melds" on the left and the "deadwoods" on the right. The algorithm was written in such a way that the most optimized result is guranteed. If you want to sort manually, you can
click on card A first, and then on Card B, then Card A will be placed just on the right of Card B.

How to Knock: When you are allowed to "knock", there will be a grey box on the right, and you can just discard the card inside the box by clicking on it.

Enjoy!
