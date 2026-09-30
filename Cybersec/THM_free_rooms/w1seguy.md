### Step 0

`nc <IP> 1337`

└─$ nc 10.112.145.163 1337
This XOR encoded text has flag 1: 330a2621215623073425223a1f1b251376083132262c1969300b0e1232041536126a24153a24282c
What is the encryption key? 

### Step 1

take first 8 characters (`330a2621`) and go to cyberchef
1) from hex
2) XOR - make the key format UTF8 and put in known plaintext `THM{`
write the four character prefix somewhere - this is 4/5 characters of the actual key

### Step 2

now take the whole encoded text (330a...282c) and go to cyberchef
1) from hex
2) XOR - make the format UTF8 and put in the four character prefix
guess the last character (a-z,A-Z, 0-9) - this will take at most ~50 tries
you will be always looking at the output hoping for `THM{some_flag}` especially the curly bracket at the end

### almost there!

this was flag1, now give the correct key to the server and grab flag2

What is the encryption key? gBkZQ
Congrats! That is the correct key! Here is flag 2: THM{BrUt3_ForC1nG_XOR_cAn_B3_FuN_nO?}
