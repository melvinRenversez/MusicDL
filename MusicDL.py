
def main():
     run = True
     while run == True:

          cmd = input("[*]--# ")

          read(cmd)


          if cmd == "quit":
               run = False
          elif cmd == "show":
               show()
          else:
               read("Unvalid Command")

def install():
     pass

def search():
     pass

def show():
     with open("link.txt") as f:
          links = f.read()
          links = links.split("\n")
          range = len(links)
          for i in range():
               print(i)
               read(links[i])


def read(text):
     print("[*]  --> " + text)

main()

