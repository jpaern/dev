{-# LANGUAGE BangPatterns #-}

module Main (main) where

-- class MyMon a where
--   mempty :: a
--   mappend :: a -> a -> a

data Tree2 a
  = Nil2
  | Leaf a
  | Branch (Tree2 a) (Tree2 a)
  deriving (Show)

data MyFunctor a = MySomething a deriving (Show)

instance Functor MyFunctor where
  fmap f (MySomething x) = MySomething (f x)

instance Functor Tree2 where
  fmap _ Nil2 = Nil2
  fmap f (Leaf a) = Leaf (f a)
  fmap f (Branch l r) = Branch (fmap f l) (fmap f r)

data Tree a
  = Nil
  | Node a (Tree a) (Tree a)
  deriving (Show)

instance Functor Tree where
  fmap _ Nil = Nil
  fmap f (Node a l r) = Node (f a) (fmap f l) (fmap f r)

foo :: Int -> Int -> Int
foo x !y = x * 2

main :: IO ()
main = do
  putStrLn "***********************************************"
  putStrLn "Start"
  putStrLn "***********************************************"
  let t1 = MySomething 45
  print t1
  print (fmap (* 2) t1)
  putStrLn "Start Tree"
  let tr1 = Node 5 (Node 3 Nil Nil) (Node 7 Nil Nil)
  print tr1
  print (fmap (* 2) tr1)
  print (foo 128 undefined)
  putStrLn "***********************************************"
  putStrLn "End"
  putStrLn "***********************************************"

-- let myTree = Node 5 (Node 3 Nil Nil) (Node 7 Nil Nil)
-- print myTree
