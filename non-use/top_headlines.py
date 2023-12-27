from newsapi import NewsApiClient
import requests

# Initialize the NewsApiClient
api_key = '785379e735a84282af1c6b35cf335a59'
newsapi = NewsApiClient(api_key=api_key)

def get_top_headlines(source=None, category=None, country=None):
    """Fetch the top headlines based on source, category or country."""
    return newsapi.get_top_headlines(
        sources=source,
        category=category,
        country=country,
        language='en'
    )

def extract_headlines(response):
    """Extract and return the headlines from the response."""
    articles = response.get('articles', [])
    return [article['title'] for article in articles]

def fetch_headlines_by_category():
    categories = ['news', 'sports', 'entertainment', 'technology', 'business']
    headlines_by_category = {}
    
    # Fetch headlines for each category and store them in the dictionary
    for category in categories:
        if category == 'news':
            # Since there's no direct "news" category, we'll combine headlines from multiple sources
            bbc_news = extract_headlines(get_top_headlines(source='bbc-news'))
            us_news = extract_headlines(get_top_headlines(country='us'))
            google_news = extract_headlines(get_top_headlines(source='google-news'))
            headlines_by_category[category] = bbc_news + us_news + google_news
        else:
            headlines_by_category[category] = extract_headlines(get_top_headlines(category=category))
    
    return headlines_by_category

def display_headlines_by_category():
    headlines = fetch_headlines_by_category()
    for category, headlines_list in headlines.items():
        print(f"{category.title()} News:")
        for idx, headline in enumerate(headlines_list, 1):
            print(idx, headline)
        print()

# Driver code
if __name__ == '__main__':
    display_headlines_by_category()

# Sample Return: 
# News News:
# 1 South African hostage Gerco van Deventer freed by al-Qaeda militants
# 2 Caroline Aherne: New unseen photos of ‘a light that didn’t shine long enough’
# 3 Wright to leave MOTD as pundit at end of season
# 4 Seven-stone turkey dog used to guard Somerset flock
# 5 Israel - Hamas war: France calls for 'immediate and durable' Gaza truce
# 6 NBA legend Kareem Abdul-Jabbar suffers broken hip after fall in Los Angeles
# 7 Why US-Palestinian families are having 'the talk'
# 8 Israel-Gaza latest news: Netanyahu insists war is only way to secure release of hostages
# 9 Why Covid is still flooring some people
# 10 The secret sauce for Taiwan's chip superstardom
# 11 Demi Lovato engaged to musician Jutes after one year of dating: See her massive ring - Page Six
# 12 Israel faces new calls for truce after killing of hostages raises alarm about its conduct in Gaza - The Associated Press
# 13 South Korea's military says North Korea has fired a ballistic missile toward its eastern waters - The Associated Press
# 14 Andy Reid and Patrick Mahomes fined a combined $150,000 for criticizing officials, AP source says - ABC News
# 15 Fox News Poll: Trump’s lead in GOP primary widens - Fox News
# 16 Colby Covington rates UFC 296 performance, blames Leon Edwards loss on judges’ bias - MMA Fighting
# 17 NFL Week 15 bold predictions: Giants' Tommy DeVito keeps making history, Kyle Pitts gets 100 yards - CBS Sports
# 18 Geomagnetic storm could cause Northern Lights to dance across United States - New York Post 
# 19 Chief strategist for pro-DeSantis super PAC resigns in latest high-profile departure - CNN
# 20 Alex Batty, teen missing for 6 years, returns to Britain after turning up in France - CBS News
# 21 Ignore The Tuition Sticker Price: How To Uncover Your True Cost At Any College - Forbes
# 22 71 percent of new HIV infections in those ages 10 to 19 are among girls - The Washington Post
# 23 A first-year medical student was learning about ultrasounds. She found something unexpected about her own health - CNN
# 24 Kuwait buries late emir Sheikh Nawaf in funeral attended by new ruler - Reuters
# 25 NOTEBOOK: What Lions' playoff picture looks like after win over Broncos - detroitlions.com
# 26 61 migrants drown in 'shipwreck' off Libyan coast, migration organization says - ABC News
# 27 [Removed]
# 28 Strengthening storm batters Florida with heavy rain and winds as it heads up the East Coast - CNN
# 29 Japan and ASEAN bolster ties at summit focused on security amid China tensions - The Associated Press
# 30 Powerball numbers for Saturday, Dec. 16, 2023 - Detroit Free Press
# 31 Exclusive look inside Hamas' Gaza tunnel network - Israeli forces dispatch - The Telegraph
# 32 Israel faces new calls for truce after killing of hostages raises alarm about its conduct in Gaza - The Associated Press
# 33 Fox News Poll: Trump’s lead in GOP primary widens - Fox News
# 34 Chief strategist for pro-DeSantis super PAC resigns in latest high-profile departure - CNN
# 35 ‘I miss my name’: Giuliani verdict lays bare limits of defamation law - The Guardian US
# 36 How Campuses Are Clamping Down on Pro-Palestinian Speech - The New York Times
# 37 Strengthening storm batters Florida with heavy rain and winds as it heads up the East Coast - CNN
# 38 Trump quotes Putin in bid to portray Biden as authoritarian - POLITICO
# 39 Japan is a cuddlier friend to South-East Asia than America or China - The Economist
# 40 Biden Administration Chooses Military Supplier for First Chips Act Grant - The New York Times

# Sports News:
# 1 Updates: Will Packers RBs Aaron Jones, AJ Dillon Play vs. Buccaneers? - Sports Illustrated
# 2 Report: Ja'Marr Chase has AC joint sprain, will have more tests Sunday - NBC Sports
# 3 Fantasy football Week 15 inactives: Who's in and who's out? - ESPN
# 4 Gavaskar's verdict on Rohit-led India's chances of maiden Test series win in SA - Hindustan Times
# 5 Kareem Abdul-Jabbar falls and breaks hip at Los Angeles concert - WXYZ 7 Action News Detroit
# 6 Report: Dolphins will let Tyreek Hill decide whether to play with ankle injury - NBC Sports
# 7 Former 5-star N.J. QB, Rutgers legacy to transfer to local rival led by ex-Scarlet Knights assistants - NJ.com
# 8 Andy Reid and Patrick Mahomes fined a combined $150,000 for criticizing officials, AP source says - ABC News
# 9 Colby Covington rates UFC 296 performance, blames Leon Edwards loss on judges’ bias - MMA Fighting
# 10 NFL Week 15 bold predictions: Giants' Tommy DeVito keeps making history, Kyle Pitts gets 100 yards - CBS Sports
# 11 IPL 2024: Nine Jammu and Kashmir Players Shortlisted for Auctions - Kashmir Life
# 12 Jake Browning on Bengals comeback win over Vikings: 'They never should have cut me' - CBS Sports
# 13 Russini: What I’m hearing in NFL Week 15 on the league coaching carousel and more - The Athletic
# 14 Real Madrid vs Villarreal, 2023 La Liga: Predicted lineups - Managing Madrid
# 15 1st ODI: Arshdeep Singh, Avesh Khan star in India's crushing win over South Africa - IndiaTimes
# 16 Patriots Rumors: New Details About Robert Kraft’s Bill Belichick Plan - NESN
# 17 Sean Payton downplays sideline flare-up with Russell Wilson: ‘I was upset about the call’ - The Athletic
# 18 Explained: What Led To Mumbai Indians' Captain Change From Rohit Sharma To Hardik Pandya? - NDTV Sports
# 19 1st ODI: Shreyas Iyer's bat goes flying to square-leg after losing grip | Cricket News - Times of India - IndiaTimes
# 20 Steph Curry makes history with 3,500th three-pointer in Golden State Warriors win against the Brooklyn Nets - CNN

# Entertainment News:
# 1 Demi Lovato engaged to musician Jutes after one year of dating: See her massive ring - Page Six
# 2 [Removed]
# 3 Princess Kate’s Heartfelt Message Ahead of Christmas Carol Service - The Royal Family Channel
# 4 Bryant Gumbel on wrapping up HBO's "Real Sports" - CBS Sunday Morning
# 5 FULL MATCH — CM Punk & Kofi Kingston vs. The Legacy — World Tag Team Titles: Raw, Oct. 27, 2008 - WWE
# 6 Promo of Salaar team’s special interview with Rajamouli is out now - 123telugu
# 7 'Dunki' to have a show at 6:55 am at Gaiety Galaxy which is the earliest show for a Shah Rukh Khan film - IndiaTimes
# 8 Parenting advice: My mom just dropped a bomb about what she "expects" of me. I'm shocked. - Slate
# 9 Bigg Boss Telugu 7: Amardeep Chowdary to quit the finale for Ravi Teja's movie offer? - Times of India
# 10 Samantha Prabhu was asked if she would ever marry again, here's how she reacted - India Today
# 11 If You Hear This Wham! Song, You've Lost - Newser
# 12 'Weekend Update': Michael Che Trolls Colin Jost With A Wicked Scasrlett Johansson Joke - HuffPost
# 13 Namrata Shirodkar Shares Special Note For Son Gautham Heading To New York For Higher Studies - NDTV Movies
# 14 Shreyas Talpade to be Discharged Soon From Hospital; Shares Filmmaker Sohum Shah - The Quint
# 15 Colin Burgess Dies: Founding Member Of Australian Rockers AC/DC Was 77 - Deadline
# 16 Aayush Sharma's car involved in accident, actor wasn't inside; police files FIR - Hindustan Times
# 17 Mötley Crüe's Nikki Sixx says Wyoming move has been ‘fantastic’: ‘Can't think of a place I'd rather be’ - Fox News
# 18 Jeffrey Epstein Never Stopped Abusing Women—and His VIP Circle Helped Make It Possible - The Wall Street Journal
# 19 Weekly Horoscope Readings for Every Zodiac Sign: Dec 17–23 - The Cut
# 20 Record-breaking! Prabhas gets a 120 feet cut-out in Mumbai for 'Salaar Part 1: CeaseFire' - IndiaTimes

# Technology News:
# 1 Year Ender 2023 Motorola Edge 40 To POCO F5, Best Midrange Smartphones Under 30,000 Launched This Year - Jagran English
# 2 ‘Sea Of Stars’ Will Remove The Completionist’s Cameo, His Own Game Of The Year - Forbes
# 3 From Iconic Weapons to Operator Customization – Here's What Advanced Warfare x Call of Duty: Modern Warfare 3 Crossover Event May Have in Store for Players From Iconic Weapons to Operator Customization – Here's What Advanced Warfare x - EssentiallySports
# 4 New Samsung Leak Reveals Stunning Galaxy S24 Design Decisions - Forbes
# 5 Quordle 692 answer for December 17: Check Quordle hints, clues, solutions - HT Tech
# 6 Instagram adds backdrop - a new AI editing tool for photo backgrounds | Deets here - India TV News
# 7 Apple 2024 Plans: New Low-End AirPods, Vision Pro, Larger iPhone 16, OLED iPad - Bloomberg
# 8 Avatar: Frontiers of Pandora - the big developer tech interview - Eurogamer.net
# 9 VC Firm Founder Reveals Biggest Investment Secrets! - YourStory
# 10 iPhone 15 Screen time will save you from weak eyesight; know how to manage it - step-by-step guide - HT Tech
# 11 Best TVs of 2023 - CNET
# 12 Readwise Reader is the ultimate app for reading the internet - The Verge
# 13 NVIDIA GeForce RTX 4090 GPUs Listed As RTX 4090 SUPER By European Retailer - Wccftech
# 14 This Firefox for Android feature you've been begging for is finally here - Android Police
# 15 Nothing Phone 2a Launch Date, Price, Specifications, First Look Leaked; All About Upcoming Phone With Real-Life Photos - Jagran English
# 16 Apple releases 1st public beta of iOS 17.3 with stolen device protection - ETTelecom
# 17 Warning! Apple Advises Against Using Non-Certified Chargers for Your Apple Watch - News18
# 18 The Last of Us Online Devs Tease their Canceled Game: ‘It Was the Highlight of My Career’ - Wccftech
# 19 Asus ROG Phone 8 to launch on January 9, 2024: Here’s what we know so far - Times of India
# 20 Weekly poll results: OnePlus 12 gets a better reception than its predecessor - GSMArena.com news - GSMArena.com

# Business News:
# 1 Understaffed and neglected: How real estate investors reshaped assisted living facilities - The Washington Post
# 2 Mcap Of 9 Most Valued Firms Jumps Rs 2.26 Lakh Cr; TCS, Infosys Biggest Gainers - News18
# 3 Federal prosecutors are investigating allegation that Jimmy Haslam attempted to bribe Pilot executives - NBC Sports
# 4 Trade Setup for December 18: What next for the Nifty 50 after best weekly run in six years? - CNBCTV18
# 5 Zee Entertainment requests Sony India to extend the deadline for merger | Mint - Mint
# 6 Elon Musk’s Big Lie About Tesla Is Finally Exposed - Rolling Stone
# 7 This CEO's bonus to be ₹905 crore if he meets one condition - Hindustan Times
# 8 Public Sector Banks may see further consolidation - BusinessLine
# 9 Travelling for Xmas, New Year? How Delhi, Mumbai, Bengaluru & Hyderabad airports have ramped up infrastru - IndiaTimes
# 10 5 Cars we Miss in India! » MotorOctane - MotorOctane
# 11 Germany Ends EV Subsidies In Latest Blow To Tesla - Investor's Business Daily
# 12 GenAI can add $1.2-1.5 trillion to India's GDP by 2030: EY report - Business Standard
# 13 5 Highly Anticipated New Cars Coming Soon - Maruti To Tata - GaadiWaadi.com
# 14 'You've got to work at McDonald's all day': This young Indianapolis man owes $36K on a car loan — but can barely make that in a single year. The Ramsey Show offered him a reality check - Yahoo Finance
# 15 DOMS Industries IPO Allotment on December 18: Check GMP Today, Know How To Check Status - News18
# 16 Post Adani takeover, ACC-Ambuja Cement EBITDA rises to Rs 1,350/tonne - Moneycontrol
# 17 The S&P 500 Is About to Do Something It Has Only Done 9 Times Before. History Says the Stock Market Will Do This Next - The Motley Fool
# 18 Ignore The Tuition Sticker Price: How To Uncover Your True Cost At Any College - Forbes
# 19 Market Trading Guide: Tata Steel, SBI among 5 stock recommendations for Monday - Stock Ideas - The Economic Times
# 20 Grandparents spoiling grandchildren with holiday gifts? Tips to help. - USA TODAY