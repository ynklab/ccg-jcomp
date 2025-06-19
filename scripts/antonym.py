from sexpdata import loads
import subprocess
import re

SEM_INFO = 3
dic_file_name = "./dict/ContentWAD.dic"


def search_antonym(adj):
    cmd = "grep " + "\" " + adj + " \" " + dic_file_name
    output = (subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True) \
              .communicate()[0].decode("utf-8"))
    if "反義" in output:
        data = loads(output)
        sem_info = data[1][SEM_INFO][1]
        sem_info = sem_info.split(" ")
        for entry in sem_info:
            if "反義" in entry:
                antonyms = (entry[3:]).split(";")
                antonyms = map(lambda x: re.sub(".*:", "", x), antonyms)
                antonyms = map(lambda x: re.sub("\/.*", "", x), antonyms)
                antonyms = list(antonyms)
        return antonyms
    elif adj == "背が高い":
        return ["背が低い"]
    elif adj == "背が低い":
        return ["背が高い"]
    else:
        return []


if __name__ == "__main__":
    print(search_antonym("長い"))