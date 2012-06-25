import re

def slugfy(text, separator):
  """ Return a slug version of a string, separated by separator
  """
    ret = ""
    for c in text.lower():
    try:
        ret += htmlentitydefs.codepoint2name[ord(c)]
    except:
        ret += c
 
    ret = re.sub("([a-zA-Z])(uml|acute|grave|circ|tilde|cedil)", r"\1", ret)
    ret = re.sub("\W", " ", ret)
    ret = re.sub(" +", separator, ret)
 
    return ret.strip()