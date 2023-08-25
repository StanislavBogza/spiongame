import telebot, time, random
from telebot import TeleBot, types

telebot_token = '6494290862:AAGezRVAAJ_cDuASHKycLe68Z83ySqCc3HY'
bot = telebot.TeleBot(token=telebot_token, parse_mode=None)
authorized_users = {}
registered_users_file = "registered_users"
admin_users_file = "admin_users"

live_game = []


def update_registered_users_file():  #Se adauga un user nou
  with open(registered_users_file, "w") as file:
    for user_id, username in authorized_users.items():
      file.write(f"{user_id} @{username}\n")


def load_authorized_users_file():  #Aici se încarcă în memorie toti userii
  try:
    with open(registered_users_file, "r") as file:
      for line in file:
        user_id, username = line.strip().split()
        authorized_users[int(user_id)] = username
  except FileNotFoundError:
    pass


def extract_random_word(orase):
  try:
    with open(orase, 'r') as file:
      words = file.readlines()
      random_word = random.choice(words).strip()
      return random_word
  except FileNotFoundError:
    print(f"File '{orase}' not found.")


def generate_spion():
  spion = random.choice(live_game)
  return spion


@bot.message_handler(commands=['start']
                     )  #Mesaj de Start Bot sau după Resetare chat
def start_message_handler(message):
  user_id = message.from_user.id
  if user_id in authorized_users:
    bot.reply_to(message, "Bine ai revenit în Spion Game !")
    if live_game:
      bot.send_message(message.chat.id, "Cineva este in joc")
    else:
      pass

  else:
    bot.reply_to(
        message,
        "Nu ai acces, adresează-te la @stabogza sau înregistrează-te cu /register"
    )
  print(live_game)


@bot.message_handler(commands=['go'])
def go_message_handler(message):
  user_id = message.from_user.id
  nume = message.from_user.first_name

  if user_id in authorized_users:
    if user_id not in live_game:
      live_game.append(user_id)
      first_name_live = []
      if len(live_game) > 1:
        bot.reply_to(
            message,
            f"Te-ai conectat. În total sunt {len(live_game)} persoane")
      else:
        bot.reply_to(
            message,
            f"Te-ai conectat, esti primul jucator, asteapta-i pe ceilalti")
    else:
      bot.reply_to(message, "Ești deja în joc, si apesi intraiurea?")
  else:
    bot.reply_to(
        message,
        "Nu ai acces, adresează-te la @stabogza sau înregistrează-te cu /register"
    )

  print(live_game)
  for id in live_game:
    if id != user_id:
      bot.send_message(
          id,
          f"{nume} s-a conectat in joc, in total sunt {len(live_game)} persoane "
      )


@bot.message_handler(commands=['incepe'])
def incepe_message_handler(message):
  user_id = message.from_user.id
  if user_id == 462716859:
    orase = "orase.txt"
    word = extract_random_word(orase)
    if len(live_game) < 1:
      bot.send_message(462716859, "Nu sunt destui jucatori")
    else:
      spion = generate_spion()
      live_game.remove(spion)

      for user_id in live_game:
        bot.send_message(user_id, f"Cuvantul este {word}")
      bot.send_message(spion, "Tu esti SPIONUL")
      live_game.append(spion)
  else:
    bot.send_message(message.chat.id, "Nu ai acces la comanda")
  print(live_game)


@bot.message_handler(commands=['stop'])
def stop_message_handler(message):
  user_id = message.from_user.id
  if user_id == 462716859:
    live_game.clear()  #sterge lista, opreste jocul
    bot.reply_to(message, "jocul s-a terminat")
  else:
    bot.reply_to(message, "Nu ai acces la comanda")
  print(live_game)


@bot.message_handler(commands=['register'])  #Cerere pentru a putea juca
def register_message_handler(message):
  user_id = message.from_user.id
  if user_id not in authorized_users:
    bot.send_message(
        462716859,
        f"""Userul {message.from_user.first_name} {message.from_user.last_name} - @{message.from_user.username} cere sa fie inregistat, id lui este {message.from_user.id}"""
    )
  else:
    bot.reply_to(message, "Esti deja inregistrat/a")


@bot.message_handler(commands=['adduser'])  #Adminii adauga userii
def add_user_handler(message):
  user_id = message.from_user.id
  if user_id == 462716859:
    try:
      command, new_user_id, username = message.text.split()
      authorized_users[new_user_id] = username
      update_registered_users_file()
      load_authorized_users_file()
      bot.reply_to(message,
                   f"User {new_user_id} with username @{username} added.")
      bot.send_message(
          new_user_id, """Ai fost adaugat/a in jocul Spion 
apasa /go pentru a incepe jocul""")
    except ValueError:
      bot.reply_to(message, "Format incorect. Use: /adduser user_id username")
  else:
    bot.reply_to(message, "Nu ai acces la această comandă")


try:  #Aici botul ruleaza continuu
  if __name__ == '__main__':
    print('Botul Spion ruleaza...')
    load_authorized_users_file()  # Load authorized users from the file
    while True:
      try:
        bot.polling(none_stop=True)
      except Exception as e:
        print(f"An error occurred: {e}")
        print("Retrying in 10 seconds...")
        time.sleep(10)
except ValueError:
  print('Ceva erori iaca')
