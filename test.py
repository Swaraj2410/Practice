import streamlit as st
import pandas as pd
import base64
import requests
import time
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon
nltk.download('vader_lexicon')

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Function to get real-time weather data
def get_weather(city):
    API_KEY = "7a2bc514b43fc8dc820ae1566673cf29"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        if response.get("cod") == 200:
            weather = {
                "Temperature": f"{response['main']['temp']}°C",
                "Condition": response["weather"][0]["description"].capitalize(),
                "Humidity": f"{response['main']['humidity']}%",
                "Wind Speed": f"{response['wind']['speed']} m/s"
            }
            return weather
        else:
            return {"Error": "Weather data not available"}
    except:
        return {"Error": "Failed to fetch data"}

# Function to encode image in base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"Error: File not found at {image_path}")
        return ""

# Sidebar with Weather Updates
st.sidebar.header("🌦️ Real-Time Weather Updates")
cities = ["Manali", "Darjeeling", "Munnar"]
for city in cities:
    weather_data = get_weather(city)
    st.sidebar.subheader(f"📍 {city}")
    for key, value in weather_data.items():
        st.sidebar.write(f"**{key}:** {value}")

# Function to load dataset
@st.cache_data
def load_data():
    file_path = r"C:\\Users\\swara\\Downloads\\Final\\Dataset.xlsx"
    return pd.read_excel(file_path)

df = load_data()


# Ensure Price Column is Numeric
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

# Encode background image
bg_image_path = r"C:\\Users\\swara\\Downloads\\Final\\hot1.avif"
bg_image_base64 = get_base64_image(bg_image_path)

# Inject custom CSS for background image
if bg_image_base64:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/avif;base64,{bg_image_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        .block-container {{
            background: rgba(0, 0, 0, 0.6);
            padding: 20px;
            border-radius: 10px;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("Background image not found. Please check the file path.")

# 🏨 Smart Accommodation Finder with Maps

st.title(" Smart Accommodation Finder")

destination = st.selectbox("📍 Select Destination", df["Destination"].unique())
price_range = st.radio("💰 Select Price Range", ["₹0 - ₹3000", "₹3001 - ₹6000", "₹6001 and above"])
all_amenities = sorted(set(",".join(df["Amenities"].dropna()).split(",")))
selected_amenities = st.multiselect("🛎️ Select Amenities", all_amenities)
checkin_date = st.date_input("📅 Select Check-in Date")
checkout_date = st.date_input("📅 Select Check-out Date")

if checkin_date >= checkout_date:
    st.warning("⚠️ Check-out date must be after the Check-in date.")

# Filter hotels based on price range
st.write("Debug: Filtering hotels based on price range...")
if price_range == "₹0 - ₹3000":
    filtered_df = df[(df["Destination"] == destination) & (df["Price"] <= 3000)]
elif price_range == "₹3001 - ₹6000":
    filtered_df = df[(df["Destination"] == destination) & (df["Price"].between(3001, 6000, inclusive="both"))]
else:
    filtered_df = df[(df["Destination"] == destination) & (df["Price"] > 6000)]

# Filter based on selected amenities
if selected_amenities:
    filtered_df = filtered_df[
        filtered_df["Amenities"].apply(lambda x: all(amenity in str(x) for amenity in selected_amenities))
    ]

# 🗺️ Display a Map of Filtered Hotels
st.subheader("🗺️ Map of Filtered Hotels")

if "latitude" in filtered_df.columns and "longitude" in filtered_df.columns:
    if not filtered_df.empty:
        # Create a subset of data with only latitude and longitude
        map_data = filtered_df[["latitude", "longitude"]].dropna()
        st.map(map_data)
    else:
        st.warning("⚠️ No hotels found for this destination and criteria. Try adjusting your filters!")
else:
    st.warning("⚠️ Latitude and Longitude data not available in the dataset.")

# 🏆 Top 3 Recommended Hotels Based on Sentiment Score
st.subheader("🏆 Top 3 Recommended Hotels")

if "sentiment_score" not in filtered_df.columns:
    st.error("⚠️ 'sentiment_score' column not found in dataset.")
    st.write("Available columns:", filtered_df.columns)
else:
    filtered_df["sentiment_score"] = pd.to_numeric(filtered_df["sentiment_score"], errors="coerce")
    top_hotels = filtered_df.dropna(subset=["sentiment_score"]).sort_values(by="sentiment_score", ascending=False).head(3)

    if top_hotels.empty:
        st.warning("⚠️ No hotels found for this destination and criteria. Try adjusting your filters!")
    else:
        for idx, hotel in top_hotels.iterrows():
            st.success(f"🏨 **{hotel['Hotel Name']}**")
            st.write(f"💰 **Price:** ₹{hotel['Price']}")
            st.write(f"⭐ **Ratings:** {hotel['Ratings']}")
            st.write(f"😊 **Sentiment Score:** {hotel['sentiment_score']:.2f}")
            st.write(f"📍 **Location:** {hotel['Destination']}")
            st.write(f"🛎️ **Amenities:** {hotel['Amenities']}")
            st.markdown("---")


if st.button("🔄 Refresh Results"):
    with st.spinner("Updating results..."):
        time.sleep(2)
    st.success("✅ Results updated!")
