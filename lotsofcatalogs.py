from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, Item, User

engine = create_engine('sqlite:///catalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(id = 1, name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Items for Soccer
catalog1 = Catalog(id = 1, user_id=1, name="Soccer")

session.add(catalog1)
session.commit()


item1 = Item(user_id=1, name="Two shinguards", description="Two shinguards", 
                catalog_id = 1)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Shinguards", description="A shin guard or shin pad is a \
piece of equipment worn on the front of a player's shin to protect them from injury. These are \
commonly used in sports including association football, baseball, ice hockey, field hockey, \
lacrosse, cricket, mountain bike trials, and other sports. This is due to either being required \
by the rules or laws of the sport or worn voluntarily by the participants for protective measures. ", 
                catalog_id = 1)

session.add(item2)
session.commit()

item3 = Item(user_id=1, name="Jersey", description="A jersey is an item of knitted clothing, \
traditionally in wool or cotton, with sleeves, worn as a pullover, as it does not open at the front, \
unlike a cardigan. It is usually close-fitting and machine knitted in contrast to a guernsey that is \
more often hand knit with a thicker yarn. The word is usually used interchangeably with sweater.", 
                catalog_id = 1)

session.add(item3)
session.commit()


# Items for Basketball
catalog2 = Catalog(id = 2, user_id=1, name="Basketball")

session.add(catalog2)
session.commit()


# Items for Baseball
catalog3 = Catalog(id = 3, user_id=1, name="Baseball")

session.add(catalog3)
session.commit()

item1 = Item(user_id=1, name="Bat", description="Basketball Bat", 
                catalog_id = 3)

session.add(item1)
session.commit()


# Items for Frisbee
catalog4 = Catalog(id = 4, user_id=1, name="Frisbee")

session.add(catalog4)
session.commit()


item1 = Item(user_id=1, name="Frisbee", description="A frisbee is a gliding toy or sporting item \
that is generally plastic and roughly 8 to 10 inches (20 to 25 cm) in diameter with a pronounced lip. \
It is used recreationally and competitively for throwing and catching, as in flying disc games.", 
                catalog_id = 4)

session.add(item1)
session.commit()


# Items for Snowboarding
catalog5 = Catalog(id = 5, user_id=1, name="SnowBoarding")

session.add(catalog5)
session.commit()


item1 = Item(user_id=1, name="Goggles", description=" They are often used in snow sports as well,\
and in swimming. Goggles are often worn when using power tools such as drills or chainsaws to prevent \
flying particles from damaging the eyes.", 
                catalog_id = 5)

session.add(item1)
session.commit()

item2 = Item(user_id=1, name="Snowboard", description="Snowboard.", 
                catalog_id = 5)

session.add(item2)
session.commit()

# Items for Rock Climbing
catalog6 = Catalog(id = 6, user_id=1, name="Rock Climbing")

session.add(catalog6)
session.commit()


# Items for Foosball
catalog7 = Catalog(id = 7, user_id=1, name="Foosball")

session.add(catalog7)
session.commit()


# Items for Skating
catalog8 = Catalog(id = 8, user_id=1, name="Skating")

session.add(catalog8)
session.commit()

# Items for Hockey
catalog9 = Catalog(id = 9, user_id=1, name="Hockey")

session.add(catalog9)
session.commit()


item1 = Item(user_id=1, name="Stick", description="Hockey Stick.", 
                catalog_id = 9)

session.add(item1)
session.commit()

print "added menu items!"