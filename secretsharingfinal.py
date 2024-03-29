# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 14:56:10 2021

@author: MYERSJ1
"""

from random import randrange
from math import floor, ceil

def message():
  print("This program implements sealed bid auctions with secret sharing ", end = "")
  print("using both addition and multiplication from secure multi-party ", end = "")
  print("computation to mask bids.")
  print("")
  print("It is assumed bidders are numbered in the order they placed ", end = "")
  print("their bids, and as such, a tie will result in the bidder with ", end = "")
  print("lower index winning. ")
  print("")
  pause = input("Press enter to contine. ")
  print("")

#Take as input the polynomial, the x value to evaluate at, and the modulus n
def evaluate(poly, x, n):
  output = 0
  for k in range(len(poly)):
    output += poly[k]*(x**k)
    output %= n
  return output


#Take as input the number of players, the polynomial, and the modulus n
def distribute(players, poly, n):

  #Get the polynomial evaluations at each point
  evals = []
  for k in range(1, players+1):
    evals.append(evaluate(poly, k, n))

  #Determine the longest evaluation so we can print in a table
  longest = 0
  for k in evals:
    if len(str(k)) > longest:
      longest = len(str(k))

  #Pad the longest evaluation so there is space between columns
  longest += 3

  #Print a nice table
  print(" "*longest, end = "")
  
  for k in range(1, players+1):
    print(("{:<%d}" %longest).format("A%s" %k), end = "")

  print("")

  print(("{:<%d}" %longest).format("f(x)"), end = "")
  for k in range(0, players):
    print(("{:<%d}" %longest).format(str(evals[k])), end = "")
      
  print("")

  return evals

#Display a single auctioneers shares
def display_shares(players, points):
  
  #Determine the longest evaluation so we can print in a table
  longest = 0
  for k in points:
    if len(str(k)) > longest:
      longest = len(str(k))

  #Pad the longest evaluation so there is space between columns
  longest += 3

  #Print a nice table
  print(" "*longest, end = "")
  
  for k in range(1, players+1):
    print(("{:<%d}" %longest).format("B%s" %k), end = "")

  print("")

  print(("{:<%d}" %longest).format("f(x)"), end = "")
  for k in range(0, players):
    print(("{:<%d}" %longest).format(str(points[k])), end = "")
      
  print("")


def gen_poly(degree, q, constant):
  #Create a polynomial
  poly = []
  poly.append(constant)
  for coef in range(1, degree):
    poly.append(randrange(1, q-1))

  return poly

#Inverse of x modulo n, where n is a prime
def inverse(x, n):
  return pow(x, n-2, n) #By Fermat, x^(n-1) = 1 mod n, so x * x^(n-2) = 1 mod n.


def lagrange(points, j, n):
  #Initialize the polynomial with (x-xi) where i=1 if j!=1, else 2
  if j != 0:
    x1 = points[0][0]
    poly = [-x1, 1] #Start with -x1 + 1*x
    used = 0
  else:
    x2 = points[1][0]
    poly = [-x2, 1] #Start with -x2 + 1*x
    used = 1

  #Top of the fractions, prod (x - x_k)
  for k in range(1, len(points)):
    temp_poly = []
    
    if k != j and k != used:

      xk = points[k][0] #x_i

      #Constant Term
      temp_poly.append(-xk*poly[0])

      #Middle Terms
      for i in range(0, len(poly)-1):
          
        temp_poly.append(poly[i] - poly[i+1]*xk)

      #Last Term
      temp_poly.append(poly[-1]) #last element of poly

      #Set the polynomial equal to this temp polynomial
      poly = temp_poly

  #Bottom of the fractions, prod (x_j - x_k)
  divisor = 1
  xj = points[j][0]
  for k in range(0, len(points)):
    if k != j:
      xk = points[k][0]
      divisor *= (xj - xk)

  #Multiply by inverse of denominator and the point yj
  inv = inverse(divisor, n)
  yj = points[j][1]
  for k in range(len(poly)):
    poly[k] = (poly[k] * inv * yj) % n

  return poly
    

def interpolate(points, n):
  #Initialize polynomial with all zeros
  poly = []
  for k in range(len(points)):
    poly.append(0)
  
  #Cycle through all points
  for j in range(len(points)):
    temp = lagrange(points, j, n)
    for k in range(len(temp)):
      poly[k] = (poly[k] + temp[k]) % n

  return poly

def display_poly(polynomial):
  poly = [] #Duplicate so we don't affect original
  for k in polynomial:
    poly.append(k)
  
  #Print first element
  print(poly[0], end = "")
  
  #Remove ending zero terms
  k = len(poly)-1
  while poly[k] == 0:
    del poly[k]
    k -= 1
  
  if len(poly) > 1:
    print(" + {0}x".format(poly[1]), end = "")
  index = 2
  while len(poly) > index:
    print(" + {0}x^{1}".format(poly[index], index), end = "")
    index += 1
  print("")

#Probability a compositve is determined to be prime is 4^-k
def MillerRabinCT(n, k):
    #Small prime tests for numbers that fail Miller-Rabin
    if n < 18:
        if n in [2, 3, 5, 7, 11, 13, 17]:
            return True
        return False
    
    #We first want to write n-1 as s*(2^t) for odd s
    t = 1
    while (n-1) % ( 2**(t+1) ) == 0:
        t += 1
    s = (n-1) // (2**t)
	
    #Determine the range of alpha
    if n < 341550071728321:
        if n < 1373653:
            Alpha = [2, 3]
        elif n < 3215031751:
            Alpha = [2, 3, 5, 7]
        else:
            Alpha = [2, 3, 5, 7, 11, 13, 17]
        
    elif n < 3317044064679887385961981:
        Alpha = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
        
    else:
        Alpha = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
		
        #Add in random alpha until Alpha has k elements
        for k in range(k - 13):
            Alpha.append(random.randrange(42, n-2))
            
    for a in Alpha:
    
        #Return False (not prime) if neither of the conditions is met
        if pow(a, s, n) != 1 and \
        False not in [pow(a, s*(2**i), n) != n-1 for i in range(t)]:
            return False #Definitely not prime
            
    #One of the conditions was met for all alpha in Alpha
    return True #Probably prime

#Finds a large enough prime using Miller-Rabin
def prime(minimum):

  #Start at a "random" location, so as to not leak information
  test = minimum + randrange(1, 10**10)
  if test%2 == 0:
    test += 1

  #Loop forever until we find a prime with confidence 4^(-32) or one in a billion-billion
  #1 in 10^20 chance of a false prime
  while True:
    if MillerRabinCT(test, 32):
      return test
    else:
      test += 2

#Squre matrix of dimension d, modulo n
def vandermonde_inv(d, n):
    #Create the extended Vandermonde matrix
    vdm = []
    for k in range(1, d+1):
        row = []
        for j in range(d):
            row.append(k**j)

        #Append the identity
        for i in range(k-1):
            row.append(0)
        row.append(1)
        for i in range(d-k):
            row.append(0)
                
        vdm.append(row)
  
    #Gauss reduction
    for k in range(d):
        #Make leading 1's
        inv = inverse(vdm[k][k], n)
        for column in range(k, 2*d):
            vdm[k][column] = (vdm[k][column]*inv) % n
      
        #Subtract
        for row in range(k+1, d):
            lead_coef = vdm[row][k]
            for column in range(k, 2*d):
                vdm[row][column] = (vdm[row][column] - (lead_coef*vdm[k][column])) % n

    #Jordan Reduction
    for k in range(d-1, 0, -1):
        #Subtract
        for row in range(k-1, -1, -1):
            trail_coef = vdm[row][k]
            for column in range(k, 2*d):
                vdm[row][column] = (vdm[row][column] - (trail_coef*vdm[k][column])) % n
    
    #Trim the identity matrix from the left
    output = []
    for row in vdm:
        output.append(row[d:])
    
    return output

def run():

  message()

  print("Would you like to show shares at each step? Shares of the ", end = "")
  print("multiplicative secret, additive secret, and initial bids ", end = "")
  print("will be displayed regardless of selection. ", end = "")
  show_shares = input("Enter yes or no. ").lower()
  print("")
  while show_shares not in ["yes", "y", "no", "n"]:
    show_shares = input("Please try again. Enter \"yes\" or \"no\". ")
    print("")
  
  print("Would you like to randomly generate the parameters? ", end = "")
  auto = input("Enter yes or no. ").lower()
  print("")
  while auto not in ["yes", "y", "no", "n"]:
    auto = input("Please try again. Enter \"yes\" or \"no\". ")
    print("")

  if auto in ["yes", "y"]:
    #41 is arbitrarily chosen as it allows relatively large polynomial degrees to be used
    #6 is chosen to satisfy m > 4t+1 with non-trivial positive integer t (just t > 1)
    m = randrange(10, 41) #Auctioneers
    n = randrange(2, 41) #Bidders

    k = randrange(100, 1000) #max bid

  else:

    m = input("How many auctioneers should there be? ")
    while type(m) != int:
      try:
        m = int(m)
        while m <= 5:
          m = input("This scheme requires m > 5. Please enter a larger integer. ")
      except ValueError:
        m = input("Please enter an integer. ")

    n = input("How many bidders should there be? ")
    while type(n) != int:
      try:
        n = int(n)
      except ValueError:
        n = input("Please enter an integer. ")

    k = input("What should the maximum bid be? ")
    while type(k) != int:
      try:
        k = int(k)
      except ValueError:
        k = input("Please enter an integer. ")
        
    

  alpha = randrange(1, 100) #Multiplicative secret
  delta = randrange(1, 10000) #Additive secret
  
  #Modulus for field
  q = prime(alpha*k + delta + 1)

  #Pick a threshold t := m > 4t+1. In particular, choose t close to the bound (within 3)
  t = randrange(max(2, ceil((m-1)/4)-3), ceil((m-1)/4))

  #Create a polynomial
  delta_poly = gen_poly(t, q, delta)
  alpha_poly = gen_poly(t, q, alpha)

  #Distribute delta
  print("First, auctioneers are distributed shares of some additive secret delta.")
  print("Here, delta =", delta)
  print("")
  shares_of_delta = distribute(m, delta_poly, q)
  print("")

  pause = input("Press enter to contine. ")
  print("")
  
  #Distribute alpha
  print("Then, auctioneers are distributed shares of some multiplicative secret alpha.")
  print("Here, alpha =", alpha)
  print("")
  shares_of_alpha = distribute(m, alpha_poly, q)
  print("")

  pause = input("Press enter to contine. ")
  print("")
  print("=============================================================")
  print("")

  #Auctioneer shares of bids
  auctioneer_shares = []
  for auctioneer in range(1, m+1):
      auctioneer_shares.append([])

  #Placing bids and distribute shares to auctioneers
  for bidder in range(1, n+1):
    degree = t #Alternatively could do "degree = randrange(min(5, t), t+1)" for example
    bid = randrange(1, k-1)
    
    bid_poly = gen_poly(degree, q, bid)
    print("Bidder", bidder, "placed a bid of", bid, ". Shares of bid", bidder, ":")
    print("")
    temp = distribute(m, bid_poly, q)

    for auctioneer in range(1, m+1):
      auctioneer_shares[auctioneer-1].append(temp[auctioneer-1])
    
    print("")
    pause = input("Press enter to contine. ")
    print("")
  print("=============================================================")
  print("")

  print("Auctioneers then multiply their share of alpha by their share of ", end = "")
  print("each bid. In doing so, they raise the degree of the polynomial ", end = "")
  print("representing the masked bids, so they must reduce the degree of ", end = "")
  print("the resulting polynomial using the Vandermonde inverse matrix to ", end = "")
  print("return to the original threshold.")
  print("")
  pause = input("Press enter to continue. ")
  print("")

  #Multiply shares by shares of alpha
  for i in range(m):
    for j in range(len(auctioneer_shares[i])):
      auctioneer_shares[i][j] = auctioneer_shares[i][j] * shares_of_alpha[i]

  if show_shares in ["yes", "y"]:
    for auctioneer in range(1, m+1):
      print("")
      print("Auctioneer %s's shares of each bid :" %auctioneer)
      print("")
      display_shares(n, auctioneer_shares[auctioneer-1])
      print("")
      pause = input("Press enter to continue. ")
      print("")

  print("=============================================================")
  print("")
  
  #Lower degree of poly to lower threshold again
  print("Auctioneers then redistribute, giving each auctioneer a share of these shares.")
  print("This lowers the threshold back to the original threshold of the secrets. ")
  print("")
  pause = input("Press enter to continue. ")
  print("")

  #Degree reduction
  vdminv = vandermonde_inv(m, q)
  temp_shares = []
  for bidder in range(n):
    newshares = []
    for auctioneer in range(m):
      constant = auctioneer_shares[auctioneer][bidder]
      poly = gen_poly(t, q, constant)

      evals = []
      for player in range(1, m+1):
        evals.append(evaluate(poly, player, q))
      newshares.append(evals)

    prod_shares = []
    for auctioneer in range(1, m+1):
      temp = 0
      for k in range(m):
        temp += newshares[k][auctioneer-1]*vdminv[0][k]
      temp %= q
      prod_shares.append(temp)
      
    temp_shares.append(prod_shares)

  #Swap order back to previous
  temp = []
  for auctioneer in range(m):
    shares = []
    for bidder in range(n):
      shares.append(temp_shares[bidder][auctioneer])
    temp.append(shares)

  #Return to proper name
  auctioneer_shares = temp

  if show_shares in ["yes", "y"]:
    for auctioneer in range(1, m+1):
      print("After redistribution, auctioneer %s's shares of each bid :" %auctioneer)
      print("")
      display_shares(n, auctioneer_shares[auctioneer-1])
      print("")
      pause = input("Press enter to continue. ")
      print("")

  print("=============================================================")
  print("")
  
        
  print("Finally, each auctioneer adds their share of delta to their ", end = "")
  print("share of alpha times each bid.")
  print("Press enter to continue. ")
  print("")

  #Add shares with shares of delta
  for i in range(m):
    for j in range(len(auctioneer_shares[i])):
      auctioneer_shares[i][j] = auctioneer_shares[i][j] + shares_of_delta[i]

  if show_shares in ["yes", "y"]:
    for auctioneer in range(1, m+1):
      print("After adding delta, auctioneer %s's shares of each bid :" %auctioneer)
      print("")
      display_shares(n, auctioneer_shares[auctioneer-1])
      print("")
      pause = input("Press enter to continue. ")
      print("")

  print("=============================================================")
  print("")

  all_points = []

  for bidder in range(n):
    points = []
    for auctioneer in range(1, m+1):
      points.append([auctioneer, auctioneer_shares[auctioneer-1][bidder]])

    all_points.append(points)

  masked_bids = []
  print("The auctioneers then interpolate their points to find the following ", end = "")
  print("polynomials with the constant terms representing the bids plus a hidden delta.")
  print("")
  for bidder in all_points:
    data = interpolate(bidder, q)
    display_poly(data)
    masked_bids.append(data[0])
  print("")
  pause = input("Press enter to contine. ")

  print("Hence, bidder", masked_bids.index(max(masked_bids))+1, "is the winner.")




run()