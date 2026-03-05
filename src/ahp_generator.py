import numpy as np
import json
from pathlib import Path

class AHPCalculator:
    def __init__(self):
        self.RI = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32}
        self.criteria = ['Fasilitas', 'Tenaga Medis', 'Aksesibilitas', 'Biaya']
        self.alternatives = ['RSCM', 'RS Premier Bintaro', 'RS Pondok Indah']
        
        # Matrix perbandingan kriteria
        self.criteria_matrix = np.array([
            [1.00, 2.00, 3.00, 4.00],
            [0.50, 1.00, 2.00, 3.00],
            [0.33, 0.50, 1.00, 2.00],
            [0.25, 0.33, 0.50, 1.00]
        ])
        
        # Matrix perbandingan alternatif untuk setiap kriteria
        self.alt_matrices = {
            'Fasilitas': np.array([
                [1.00, 1.50, 2.00],
                [0.67, 1.00, 1.50],
                [0.50, 0.67, 1.00]
            ]),
            'Tenaga Medis': np.array([
                [1.00, 2.00, 2.50],
                [0.50, 1.00, 1.50],
                [0.40, 0.67, 1.00]
            ]),
            'Aksesibilitas': np.array([
                [1.00, 0.80, 1.50],
                [1.25, 1.00, 1.80],
                [0.67, 0.56, 1.00]
            ]),
            'Biaya': np.array([
                [1.00, 0.80, 0.80],
                [1.25, 1.00, 1.00],
                [1.25, 1.00, 1.00]
            ])
        }

    def normalize_matrix(self, matrix):
        """Normalize a matrix to be column-wise normalized"""
        return matrix / matrix.sum(axis=0)

    def get_weights(self, matrix):
        """Get weights for the normalized matrix"""
        normalized = self.normalize_matrix(matrix)
        return np.mean(normalized, axis=1)

    def consistency_check(self, matrix, weights):
        """Consistency check for the AHP method"""
        n = len(matrix)
        lambda_max = np.sum(np.dot(matrix, weights) / weights) / n
        CI = (lambda_max - n) / (n - 1)
        CR = CI / self.RI[n]
        return CR < 0.1, CR

    def calculate(self):
        """Calculate the final results for AHP method"""
        # Calculate criteria weights
        criteria_weights = self.get_weights(self.criteria_matrix)
        is_consistent, CR = self.consistency_check(self.criteria_matrix, criteria_weights)
        
        # Calculate alternative weights for each criterion
        alt_weights = {}
        for criterion in self.criteria:
            alt_weights[criterion] = self.get_weights(self.alt_matrices[criterion])
        
        # Final scores for each alternative
        final_scores = np.zeros(len(self.alternatives))
        for i, criterion in enumerate(self.criteria):
            final_scores += criteria_weights[i] * alt_weights[criterion]
        
        return {
            'criteria_weights': dict(zip(self.criteria, criteria_weights)),
            'alternative_weights': {k: dict(zip(self.alternatives, v)) 
                                  for k, v in alt_weights.items()},
            'final_scores': dict(zip(self.alternatives, final_scores)),
            'CR': float(CR)
        }

def generate_html(results):
    """Generate an HTML report for the AHP results"""
    results_json = json.dumps(results)
    
    html_content = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistem Pendukung Keputusan Pemilihan Rumah Sakit</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-center text-gray-800 mb-2">
            Sistem Pendukung Keputusan Pemilihan Rumah Sakit
        </h1>
        <h2 class="text-xl text-center text-gray-600 mb-8">
            Menggunakan Metode Analytical Hierarchy Process (AHP) Oleh Teddy Lioner UBL 2311600130
        </h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h3 class="text-xl font-semibold mb-4">Bobot Kriteria</h3>
                <canvas id="criteriaChart"></canvas>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h3 class="text-xl font-semibold mb-4">Skor Akhir Rumah Sakit</h3>
                <canvas id="hospitalChart"></canvas>
            </div>
        </div>
    </div>
    
   <script>
    const results = {results_json};

    document.addEventListener('DOMContentLoaded', function() {{
        // Bobot Kriteria Chart
        const criteriaCtx = document.getElementById('criteriaChart').getContext('2d');
        new Chart(criteriaCtx, {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(results.criteria_weights),
                datasets: [{{
                    data: Object.values(results.criteria_weights),
                    backgroundColor: ['#4C51BF', '#48BB78', '#4299E1', '#ECC94B', '#F56565']
                }}]
            }},
            options: {{
                responsive: true,
            }}
        }});

        // Skor Akhir Rumah Sakit Chart
        const hospitalCtx = document.getElementById('hospitalChart').getContext('2d');
        new Chart(hospitalCtx, {{
            type: 'bar',
            data: {{
                labels: Object.keys(results.final_scores),
                datasets: [{{
                    label: 'Skor Akhir',
                    data: Object.values(results.final_scores),
                    backgroundColor: ['#4C51BF', '#48BB78', '#4299E1', '#ECC94B', '#F56565']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }},
                }}
            }}
        }});
    }});
</script>
</body>
</html>
""".format(results_json=results_json)

    
    # Write to file in root directory
    output_path = Path(__file__).parent.parent / 'index.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    calculator = AHPCalculator()
    results = calculator.calculate()
    generate_html(results)
    print("File index.html telah dibuat!")

if __name__ == '__main__':
    main()

