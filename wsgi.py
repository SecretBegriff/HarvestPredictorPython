from src import create_app

app = create_app()

if __name__ == "__main__":
    print("=== Harvest Predictor Backend (Modular) ===")
    app.run(debug=True, port=5000, host='0.0.0.0')