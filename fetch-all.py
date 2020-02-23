import sys, os, git, struct, glob
from git import InvalidGitRepositoryError, GitCommandError

def fetch_all(path):
    try:
        repository = git.Repo(path)
        print(repository)
        
    except InvalidGitRepositoryError:
        return
    
    for remote in repository.remotes:
        print('\t' + remote.name)
        
        for ref in remote.refs:
            if ref.name != 'origin/HEAD':
                
                print('\t\t' + ref.name)
                try:
                    refspec = ref.name.replace(remote.name + '/', '')
                    remote.fetch(refspec)
                    
                except GitCommandError:
                    return

# From https://stackoverflow.com/a/28952464.
def resolve_shortcut(file):
    with open(file, 'rb') as stream:
        content = stream.read()

        # skip first 20 bytes (HeaderSize and LinkCLSID)
        # read the LinkFlags structure (4 bytes)
        lflags = struct.unpack('I', content[0x14:0x18])[0]
        position = 0x18

        # if the HasLinkTargetIDList bit is set then skip the stored IDList 
        # structure and header
        if (lflags & 0x01) == 1:
            position = struct.unpack('H', content[0x4C:0x4E])[0] + 0x4E
        last_pos = position
        position += 0x04

        # get how long the file information is (LinkInfoSize)
        length = struct.unpack('I', content[last_pos:position])[0]

        # skip 12 bytes (LinkInfoHeaderSize, LinkInfoFlags, and VolumeIDOffset)
        position += 0x0C

        # go to the LocalBasePath position
        lbpos = struct.unpack('I', content[position:position+0x04])[0]
        position = last_pos + lbpos

        # read the string at the given position of the determined length
        size= (length + last_pos) - position - 0x02
        temp = struct.unpack('c' * size, content[position:position+size])
        target = ''.join([chr(ord(a)) for a in temp])

        return target

root = os.path.dirname(os.path.realpath(__file__))

for directory in os.listdir(root):
    fetch_all(os.path.join(root, directory))

for shortcut in glob.glob('*.lnk'):
    fetch_all(resolve_shortcut(shortcut))
    