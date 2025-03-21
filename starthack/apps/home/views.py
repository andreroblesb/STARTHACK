# apps/home/views.py
import os
import joblib
import numpy as np
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.home.models import Widget, User  # Changed imports to match updated models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from decimal import Decimal
import json
from sklearn.preprocessing import MinMaxScaler
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def landing_page(request):
    return render(request, 'landing/index.html')  # Rendering the landing page from 'home/templates/home/'

def login_page(request):
    return render(request, 'home/login.html')  # Rendering login page from 'home/templates/home/'

# @login_required
def home(request):
    context = {
        'widgets': {},
        'error': None
    }
    
    try:
        # Get all widgets from database
        widgets = Widget.objects.all()
        
        # Build widgets dictionary with complete information
        for widget in widgets:
            key_name = widget.name.lower().replace(' ', '_').replace('-', '_')
            context['widgets'][key_name + '_widget'] = {
                'id': widget.id,
                'name': widget.name,
                'source_id': widget.source_id,
                'active': widget.active,
                'position_x': widget.position_x,
                'position_y': widget.position_y,
                'width': widget.width,
                'height': widget.height,
                'cost': widget.cost
            }
        
        # Get user profile information if available
        try:
            user = User.objects.first()
            if user:
                context['user_profile'] = {
                    'name': user.name,
                    'widget_fee': user.widget_fee,
                    'cost_saving': user.costs_saved
                }
        except User.DoesNotExist:
            pass
            
        # Count active widgets
        active_count = sum(1 for widget in context['widgets'].values() if widget['active'])
        print(f"Number of active widgets: {active_count}")
        
        # retrieve fee acumulated
        try:
            user = User.objects.first()
            if user:
                context['fee'] = float(user.widget_fee)
        except User.DoesNotExist:
            context['fee'] = 0
            
        df = load_data()
        labels, scores = top_sustainable_devices(df)
        top_devices = {
        "labels": json.dumps(labels.tolist()),  
        "scores": json.dumps(scores.tolist())  
        }
        context["top_sustainable_devices"] = top_devices
        
        # get eficiency
        top_failure_devices = {
        "labels": json.dumps(labels.tolist()),
        "scores": json.dumps(scores.tolist())
        }
        
        context["top_failure_devices"] = top_failure_devices
        
        # Remove duplicate call to efficiency_metrics
        labels, actual_scores, predicted_scores, mae, mse, r2 = eficiency_metrics(df)
        
        # Debug print
        print("Efficiency Data:")
        print(f"Labels count: {labels}")
        print(f"Actual scores count: {len(actual_scores)}")
        print(f"Predicted scores count: {len(predicted_scores)}")
        
        # Format the data properly
        context["efficiency_data"] = {
            "labels": labels[:100],  # Limit data points
            "actual_scores": actual_scores[:100],
            "predicted_scores": predicted_scores[:100]
        }
        
        # Debug print
        print("Efficiency data prepared:", len(context["efficiency_data"]["labels"]))
        
        # get inneficient devices
        inefficient_labels, inefficient_scores = inefficient_devices(df)
        context["inefficient_devices"] = {
            "labels": inefficient_labels,  # No need for JSON dumps
            "scores": inefficient_scores   # No need for JSON dumps
        }
        
        print("Inefficient devices context:", context["inefficient_devices"])  # Debug print
        return render(request, 'home/index.html', context)
        
    except Exception as e:
        print("Error in home view:", str(e))  # Debug print
        context['error'] = str(e)
        return render(request, 'home/index.html', context)

def register(request):
    return render(request, 'home/register.html')  # Rendering the register page from 'home/templates/home/'

@csrf_exempt  # ⚠️ Use CSRF token instead if possible
@transaction.atomic
def remove_widget(request):
    try:
        data = json.loads(request.body)
        widget_id = data.get("widget_id")

        widget = Widget.objects.select_for_update().filter(source_id=widget_id).first()
        user = User.objects.select_for_update().first()

        if widget and user:
            if widget.active:  # Only update if widget is currently active
                widget.active = False
                widget.save()
                
                # Update fee using Decimal
                user.widget_fee = user.widget_fee - Decimal(str(widget.cost))
                user.save()

            return JsonResponse({
                "success": True,
                "message": f"Widget {widget_id} removed.",
                "new_fee": float(user.widget_fee),
                "widget_id": widget_id
            })
        else:
            return JsonResponse({"success": False, "error": "Widget or user not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
@transaction.atomic
def add_widget(request):
    try:
        data = json.loads(request.body)
        widget_id = data.get("widget_id")

        widget = Widget.objects.select_for_update().filter(source_id=widget_id).first()
        user = User.objects.select_for_update().first()

        if widget and user:
            if not widget.active:  # Only update if widget isn't already active
                widget.active = True
                widget.save()
                
                # Update fee using Decimal
                user.widget_fee = user.widget_fee + Decimal(str(widget.cost))
                user.save()

            return JsonResponse({
                "success": True,
                "message": f"Widget {widget_id} added.",
                "new_fee": float(user.widget_fee),
                "widget_id": widget_id
            })
        else:
            return JsonResponse({"success": False, "error": "Widget or user not found."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of views.py
    file_path = os.path.join(base_dir, "data", "ev3_device_data_100000.csv")  # Construct absolute path
    
    if not os.path.exists(file_path):  # Ensure the file exists
        raise FileNotFoundError(f"🚨 CSV file not found at: {file_path}")

    return pd.read_csv(file_path)


def top_sustainable_devices(df):
    # Convert timestamps
    df["sample_time"] = pd.to_datetime(df["sample_time"], errors='coerce')

    # *Check and Filter Required Columns*
    required_columns = ["device_id", "DeltaT_K", "Flow_Volume_total_m3", "AbsPower_Fb_W", "OperatingHours"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise KeyError(f"🚨 Missing columns: {missing_columns}")

    # *Drop rows where any of the required columns are NaN*
    df = df.dropna(subset=required_columns)

    # *Group by Device ID for Aggregated Analysis*
    device_df = df.groupby("device_id").agg({
        "DeltaT_K": "mean",
        "Flow_Volume_total_m3": "mean",
        "AbsPower_Fb_W": "mean",
        "OperatingHours": "mean"
    }).reset_index()

    # Ensure no NaN values before normalizing
    device_df = device_df.dropna()

    if device_df.empty:
        return [], []

    # *Normalize Values*
    scaler = MinMaxScaler(feature_range=(0, 100))
    device_df[["DeltaT_K", "Flow_Volume_total_m3", "AbsPower_Fb_W", "OperatingHours"]] = scaler.fit_transform(
        device_df[["DeltaT_K", "Flow_Volume_total_m3", "AbsPower_Fb_W", "OperatingHours"]]
    )

    # *Compute Sustainability Score (Simple Average)*
    device_df["Sustainability_Score"] = device_df[["DeltaT_K", "Flow_Volume_total_m3", "AbsPower_Fb_W", "OperatingHours"]].mean(axis=1)

    # Remove any remaining NaN values
    device_df = device_df.dropna()

    # *Sort by Sustainability Score*
    device_df = device_df.sort_values("Sustainability_Score", ascending=False)

    # *Select Top 10 Devices*
    top_devices = device_df.head(10)

    if top_devices.empty:
        return [], []

    x_labels = top_devices["device_id"].astype(str)
    
    return x_labels, top_devices["Sustainability_Score"]



def eficiency_metrics(df):
    # Convert timestamps and sort
    df["sample_time"] = pd.to_datetime(df["sample_time"])
    df = df.sort_values("sample_time")

    # *Check and Update Feature Names*
    features = ["Flow_Volume_total_m3", "AbsPower_Fb_W", "OperatingHours"]
    if not all(col in df.columns for col in features + ["DeltaT_K"]):
        raise KeyError("🚨 Some required columns are missing!")

    # *Drop rows with missing values*
    df = df.dropna(subset=["DeltaT_K"] + features)

    # *Define X (features) and y (target)*
    X = df[features]
    y = df["DeltaT_K"]

    # Path where model will be saved
    model_path = "saved_models/efficiency_model.joblib"
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    # Load or train model
    if os.path.exists(model_path):
        print("✅ Loading existing model...")
        model = joblib.load(model_path)
    else:
        print("🚀 Training new model...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=200, random_state=42)
        model.fit(X_train, y_train)
        joblib.dump(model, model_path)
        print("💾 Model saved to disk.")

    # Predict optimized efficiency
    df["Predicted_Efficiency"] = model.predict(X)

    # *Apply Rolling Average for Smoothing*
    df["Smoothed_Actual_Efficiency"] = df["DeltaT_K"].rolling(window=50, min_periods=1).mean()
    df["Smoothed_Predicted_Efficiency"] = df["Predicted_Efficiency"].rolling(window=50, min_periods=1).mean()

    # *Reduce Points for Better Visualization*
    df_sample = df.iloc[::50, :]  # Changed from 100 to 50 for more data points

    # *Evaluate Model Performance*
    # Use new test split for evaluation only if model was just trained
    if 'X_train' in locals():
        mae = mean_absolute_error(y_test, model.predict(X_test))
        mse = mean_squared_error(y_test, model.predict(X_test))
        r2 = r2_score(y_test, model.predict(X_test))
    else:
        mae = mse = r2 = None  # or load from file if you stored them

    # Simplify data format
    try:
        # Sample and format data
        df_sample = df.iloc[::100, :].copy()  # Take every 100th row
        
        # Generate simple labels and values
        labels = [t.strftime('%H:%M') for t in df_sample['sample_time']]
        actual = [round(float(x), 2) for x in df_sample['Smoothed_Actual_Efficiency'] if pd.notnull(x)]
        predicted = [round(float(x), 2) for x in df_sample['Smoothed_Predicted_Efficiency'] if pd.notnull(x)]
        
        print("Data points:", len(labels), len(actual), len(predicted))  # Debug info
        
        return labels, actual, predicted, mae, mse, r2
    except Exception as e:
        print("Error in efficiency_metrics:", str(e))
        return [], [], [], None, None, None


def inefficient_devices(df):
    try:
        # Calculate inefficiency score
        df["inefficiency_score"] = (df["AbsPower_Fb_W"] * df["OperatingHours"]) / df["Flow_Volume_total_m3"]
        
        # Group by device and get mean inefficiency
        device_stats = df.groupby("device_id")["inefficiency_score"].mean().sort_values(ascending=False)
        
        # Get top 5 inefficient devices
        top_devices = device_stats.head(5)
        
        # Convert to simple lists
        labels = [f"Device {x}" for x in top_devices.index.astype(str)]
        scores = [round(float(x), 2) for x in top_devices.values]
        
        print("Inefficient devices data:", labels, scores)  # Debug print
        return labels, scores
    except Exception as e:
        print("Error in inefficient_devices:", str(e))
        return ["No Data"] * 5, [0] * 5