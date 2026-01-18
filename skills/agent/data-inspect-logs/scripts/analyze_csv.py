import sys
import csv
import statistics

def analyze(file_path):
    print(f"📊 Analyzing: {file_path}")
    
    headers = []
    data = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print("❌ Error: File not found.")
        sys.exit(1)
        
    print(f"✅ Loaded {len(data)} records.\n")
    
    # Simple Column Analysis
    for i, col_name in enumerate(headers):
        values = [row[i] for row in data if row[i].strip() != '']
        missing_count = len(data) - len(values)
        
        print(f"--- Column: {col_name} ---")
        print(f"   Missing: {missing_count}")
        
        # Try numeric stats
        try:
            numeric_values = [float(v) for v in values]
            if numeric_values:
                avg_val = statistics.mean(numeric_values)
                max_val = max(numeric_values)
                min_val = min(numeric_values)
                print(f"   Avg: {avg_val:.2f} | Max: {max_val} | Min: {min_val}")
        except ValueError:
            # Not numeric, maybe categorical
            unique_vals = set(values)
            if len(unique_vals) < 10:
                print(f"   Values: {list(unique_vals)}")
            else:
                print(f"   Unique entries: {len(unique_vals)}")
        print("")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_csv.py <csv_file>")
        sys.exit(1)
    analyze(sys.argv[1])
