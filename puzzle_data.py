import requests
import json
from textwrap import wrap
import datetime
import pymongo


# This is the laziest least production ready code ever but w/e yolo it works
# Cue the world's longest try statement...
try:
    data = requests.get("https://puzzles-prod.telegraph.co.uk/plusword/data.json")
    data = json.loads(data.content)
    cell_data = data.get("celldata")
    words = wrap(cell_data, 5)
    solution = data.get("settings").get("solution")
    puzzle_number = data.get("meta").get("number")
    clue_data_across = data.get("cluedata").get("across")
    clue_data_down = data.get("cluedata").get("down")

    colouring = [["" for x in range(5)] for x in range(5)]
    yellow = []
    green = []
    for word_index in range(0, 5):
        # We'll use a temporary copy of the solution so that we can manipulate it.
        temp_solution = list(solution)
        for letter_index in range(0, 5):
            # If the letters match then we are correct
            current_letter = words[word_index][letter_index]
            if solution[letter_index] == current_letter:
                temp_solution.remove(current_letter)
                green.append((word_index*5)+letter_index+1)
        for letter_index in range(0, 5):
            current_letter = words[word_index][letter_index]
            # Otherwise, we need to scan through the word to see if the letter exists.
            if current_letter in temp_solution:
                temp_solution.remove(current_letter)
                yellow.append((word_index*5)+letter_index+1)

    db_data = {
        "date": datetime.date.today(),
        "puzzle_number": puzzle_number,
        "plusword_solution": solution,
        "answer_1": words[0],
        "answer_2": words[1],
        "answer_3": words[2],
        "answer_4": words[3],
        "answer_5": words[4],
        "clue_across_1": clue_data_across[0],
        "clue_across_2": clue_data_across[1],
        "clue_across_3": clue_data_across[2],
        "clue_across_4": clue_data_across[3],
        "clue_across_5": clue_data_across[4],
        "clue_down_1": clue_data_down[0],
        "clue_down_2": clue_data_down[1],
        "clue_down_3": clue_data_down[2],
        "clue_down_4": clue_data_down[3],
        "clue_down_5": clue_data_down[4],
        "yellow": yellow,
        "green": green
    }

    with open("local/pass.json") as file:
        file = json.loads(file.read())
        connection_string = file.get("admin_connection_string")
        client = pymongo.MongoClient(
            connection_string)
        db = client["PlusWord"]
        collection = db["Puzzle_Data"]  # btw I hate our naming convention, wish we were lower case gamers
        collection.insert_one(data)
except Exception as e:
    print(e)


