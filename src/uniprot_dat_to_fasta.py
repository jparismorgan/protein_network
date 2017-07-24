############
### This script modified from Lothar Wissler at https://github.com/lotharwissler/bioinformatics/blob/master/python/fasta/uniprot-dat-to-fasta.py
### Done so with the permissions granted via the The MIT License (MIT) Copyright (c) 2012 Lothar Wissler. The following is included per the License.
###
###The MIT License (MIT)
###Copyright (c) 2012 Lothar Wissler
###Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
###The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
###THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
############

def parse_until_doubleslash(fo):
  hash, end = {}, False
  line = fo.readline().strip()
  while not line.startswith("//"):
    if len(line) == 0:
      end = True
      break
    if len(line.split(" ", 1)[0]) != 2:
      key = "SEQ"
      value = line.strip().replace(" ", "")
    else:
      cols =  [e.strip() for e in line.split(" ", 1)]
      if len(cols) != 2: 
        line = fo.readline().strip()
        continue
      key, value = [e.strip() for e in line.split(" ", 1)]
    if not hash.has_key(key): hash[key] = ""
    if key != "SEQ" and len(hash[key]) > 0 and hash[key][-1] != " " and not value.startswith(" "): hash[key] += " "
    hash[key] += value
    line = fo.readline().strip()
  return hash, end
  

def uniprot_dat_to_fasta(file_path):
  dat_file = open(file_path, "r")
  fasta_file_path = file_path.split(".")[0] + ".fasta"
  print fasta_file_path
  fasta_file = open(fasta_file_path, "w")
  while 1:
    hash, end = parse_until_doubleslash(dat_file)
    if end: break
    fasta_file.write(">" + hash["ID"].split()[0] + " " + hash["OC"] + "\n")
    fasta_file.write(hash["SEQ"] + "\n")
  dat_file.close()

def main():
  uniprot_dat_to_fasta("uniprot_trembl_bacteria.dat")
  
if __name__ == '__main__':
  main()