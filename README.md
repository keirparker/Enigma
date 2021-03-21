# Enigma

An Object Oriented approach to simulating every part of the famed [Enigma](https://en.wikipedia.org/wiki/Enigma_machine) machine. 
In this project, each individual part of the machine is simulated, from PlugLeads and PlugBoards to the multiple rings and rotors (even the pesky rotor double step).

To run:
```python
Example1 = Enigma(input='HELLOWORLD', rotors=['I', 'II', 'III'], reflector='B', plugs=['HL','MO','AJ','CX','BZ','SR','NI','YW','DG','PK'], pos='AAZ', rings=['01', '01', '01'])
assert(Example1.run_machine()=="RFKTMBXVVW")

Example2 = Enigma(input='BUPXWJCDPFASXBDHLBBIBSRNWCSZXQOLBNXYAXVHOGCUUIBCVMPUZYUUKHI', rotors=['IV', 'V', 'Beta','I'], reflector='A', plugs=['PC','XZ','FM','QA','ST','NB','HY','OR','EV','IU'], pos='EZGP', rings=['18', '24', '03','05'])
assert(Example2.run_machine()=="CONGRATULATIONSONPRODUCINGYOURWORKINGENIGMAMACHINESIMULATOR")
```
## Advanced Enigma

In order for my idea for my extension to work, I needed to add two more characters to my plugboard, rotors and reflectors (This can be seen in rotor_mapping_ext.csv, as well as throughout advanced_work.py where code on notches, ring settings, initial positions and moving rotors needed to be modified). This naturally changes the calculations we see above, so we need to recalculate!

```python
n = 28
for m in range(1,int(n/2)+1):
    print(f"{str(m)} pairs  \t: {str( math.factorial(n) /(math.factorial(n-(2*m))* math.factorial(m) *2**m))}")
```
```
1 pairs  	: 378.0
2 pairs  	: 61425.0
3 pairs  	: 5651100.0
4 pairs  	: 326351025.0
5 pairs  	: 12401338950.0
6 pairs  	: 316234143225.0
7 pairs  	: 5421156741000.0
8 pairs  	: 61665657928875.0
9 pairs  	: 452214824811750.0
10 pairs  	: 2034966711652875.0
11 pairs  	: 5179915266025500.0
12 pairs  	: 6474894082531875.0
13 pairs  	: 2988412653476250.0
14 pairs  	: 213458046676875.0
```
The addition of the two new characters pushes the optimal number of plugleads to a whopping 12. Because of this, I have changed the lead limit coded into my Plugboard class to 12. And the total number of plugboard combinations have increased by well over an order of magnitude.

Now the reason for adding in these two extra characters, which I will now reveal to be 'SPACE' and '.', was to massively build on the functionality of such a complex machine, and utilise the advantages that come with the building one digitally. Having the ability to input spaces and full stops now allows FULL SENTENCES to be read into the enigma machine to be encrypted/decrypted where appropriate.

```python
from advanced_work import *

Advanced_demo = Advanced_Enigma(input='HOFFMANS BIRTHDAY IS THE TWENTIETH OF JANUARY. HE WILL BE THREE YEARS OLD SOON.', rotors=['I', 'II', 'III'], reflector='B', plugs=['AB','.D','_F','GH','IJ','KL','MN','OP','QR','ST','UV','XZ'], pos='_A.', rings=['02', '03', '04'])

encrypt_demo = Advanced_demo.run_machine()

decrypt_demo = Advanced_Enigma(input=encrypt_demo, rotors=['I', 'II', 'III'], reflector='B', plugs=['AB','.D','_F','GH','IJ','KL','MN','OP','QR','ST','UV','XZ'], pos='_A.', rings=['02', '03', '04'])

out = decrypt_demo.run_machine()

print(encrypt_demo)

print(out)
```
```
GATLTBKENLNFNFBTCNAQBZFCMHBQYF TMNEKVMZMOHDYEENLGIXKJJUTZPKR OR.DMENZRROGBLCSLS
HOFFMANS BIRTHDAY IS THE TWENTIETH OF JANUARY. HE WILL BE THREE YEARS OLD SOON.
```
Now this is great and all. But it wouldnt exactly help us win the war. What comes next would be bloody handy at a time when most german speakers are pointing guns at you.

```python
Advanced_demo2 = Advanced_Enigma(input='HOFFMANS BIRTHDAY IS THE TWENTIETH OF JANUARY. HE WILL BE THREE YEARS OLD SOON.', rotors=['I', 'II', 'III'], reflector='B', plugs=['AB','.D','_F','GH','IJ','KL','MN','OP','QR','ST','UV','XZ'], pos='_A.', rings=['02', '03', '04'])

encrypt_demo2 = Advanced_demo2.run_machine()

decrypt_demo2 = Advanced_Enigma(input=encrypt_demo2, rotors=['I', 'II', 'III'], reflector='B', plugs=['AB','.D','_F','GH','IJ','KL','MN','OP','QR','ST','UV','XZ'], pos='_A.', rings=['02', '03', '04'])

out2 = decrypt_demo2.translate_and_decrypt('en','de')

print(encrypt_demo2)

print(out2)
```
```
GATLTBKENLNFNFBTCNAQBZFCMHBQYF TMNEKVMZMOHDYEENLGIXKJJUTZPKR OR.DMENZRROGBLCSLS
HOFFMANS GEBURTSTAG IST DER 20. JANUAR. Er wird bald drei Jahre alt sein.
```
Awesome! Now all german speakers can also celebrate Hoffmans birthday. But perhaps it would be more useful to see this in a case scenario (disclaimer- This will probably not be factually accurate).

### Case Scenario
The year is 1942 and Turing has just cracked the enigma machine to much joy and relief. Just in time too, as super secret english spies have reported that the german forces are moving. They just have no idea when.

One of these spies, Nathaniel McCann has intercepted an encrypted message that he claims to be relevant.

Message: 'ZSXHRUXWYTWRXHWQUHUAZMW GHQLNQZAS VSPPVYHXGUKLKWNJAUAQONMACTXI TU.RNUGVWIPSAGTPXAFCSNTFGQYNKM XIXWJFXAEKHZM'

Using the computational prowess of Turing, we can crack the code below and strategise accordingly.

```python
Advanced_demo3 = Advanced_Enigma(input='ZSXHRUXWYTWRXHWQUHUAZMW GHQLNQZAS  VSPPVYHXGUKLKWNJAUAQONMACTXI TU.RNUGVWIPSAGTPXAFCSNTFGQYNKM XIXWJFXAEKHZM', rotors=['IV', 'II', 'III'], reflector='A', plugs=['KL','MN','OP','QR','ST','UV','XZ'], pos='ZDT', rings=['03', '04', '18'])

encrypt_demo3 = Advanced_demo3.run_machine()

print(encrypt_demo3)
```
```
DIE TRUPPEN AN DER WESTFRONT WERDEN IN EINER WOCHE VORRUCKEN. ES IST EIN SUPER RIESIGES DEUTSCHES GEHEIMNIS.
```
Oh no! The decyphered code is in german! As the English are famous for refusing to learn other languages and very very early mentions of something called 'Brexit' have stopped what few germans the English were friends with from talking to them, this is quite a disaster.

But hang on, word is there's a student from the University of Bath that can offer some help. Let's try his more advanced machine and see what happens.

```python
Advanced_demo4 = Advanced_Enigma(input='ZSXHRUXWYTWRXHWQUHUAZMW GHQLNQZAS  VSPPVYHXGUKLKWNJAUAQONMACTXI TU.RNUGVWIPSAGTPXAFCSNTFGQYNKM XIXWJFXAEKHZM', rotors=['IV', 'II', 'III'], reflector='A', plugs=['KL','MN','OP','QR','ST','UV','XZ'], pos='ZDT', rings=['03', '04', '18'])

encrypt_demo4 = Advanced_demo4.translate_and_decrypt('de','en')

print(encrypt_demo4)
```
```
THE TROOPS ON THE WEST FRONT WILL ADVANCE IN A WEEK. IT'S A SUPER HUGE GERMAN SECRET.
Fantastic! The encrypted message turned out to contain german military secrets! We can get this to Churchill pronto.
```

4
df.plot(kind='bar')
<AxesSubplot:>

There is already functionality for this in the 'detection' algorithims the translation library uses, but there would be definite value in creating such a visual aid.

The end
Thanks for the opportunity to take on this project, it was a lot of fun and I learned a lot.
