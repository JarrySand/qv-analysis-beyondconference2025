document.addEventListener('DOMContentLoaded', function() {
    createBuriedVoicesChart();
    createPreferenceIntensityHeatmap();
    createPreferenceComparisonChart();
    createBudgetAllocationChart();
    createGiniCoefficientChart();
    createLorenzCurveChart();
    createPercentageComparisonChart();
    createVoteComparisonChart();
});

function createBuriedVoicesChart() {
    const chartContainer = document.getElementById('buried-voices-chart');
    
    const projects = [
        'Bio Rice Field Project',
        'Chiba Youth Center PRISM',
        'Awaji Island Quest College',
        'Inatori Art Center Plan',
        'Para Travel Support Team',
        '#vote_for Project',
        'JINEN TRAVEL'
    ];
    
    const buriedVotes = [37, 35, 33, 29, 26, 22, 20];
    
    const data = [{
        x: projects,
        y: buriedVotes,
        type: 'bar',
        marker: {
            color: '#3498db',
            opacity: 0.8
        }
    }];
    
    const layout = {
        title: '「埋もれた声」の数（一人一票方式では反映されない強い選好）',
        xaxis: {
            title: 'プロジェクト名',
            tickangle: -45
        },
        yaxis: {
            title: '埋もれた声の数'
        },
        margin: {
            l: 50,
            r: 50,
            b: 150,
            t: 80,
            pad: 4
        }
    };
    
    Plotly.newPlot(chartContainer, data, layout, {responsive: true});
}

function createPreferenceIntensityHeatmap() {
    const chartContainer = document.getElementById('preference-intensity-chart');
    
    const projects = [
        'Chiba Youth Center PRISM',
        'Awaji Island Quest College',
        'Bio Rice Field Project',
        'Para Travel Support Team',
        'Inatori Art Center Plan',
        'JINEN TRAVEL',
        '#vote_for Project'
    ];
    
    const intensities = ['1', '2', '3', '4', '5', '6', '7', '8', '9'];
    
    const zValues = [
        [8, 12, 15, 20, 18, 14, 10, 12, 8],  // PRISM
        [10, 15, 20, 25, 15, 12, 8, 6, 4],   // Quest College
        [12, 18, 16, 15, 14, 12, 10, 9, 8],  // Rice Field
        [14, 16, 20, 18, 12, 10, 10, 8, 6],  // Para Travel
        [15, 20, 18, 15, 12, 10, 8, 6, 4],   // Art Center
        [16, 18, 16, 14, 12, 10, 8, 6, 4],   // JINEN
        [20, 25, 20, 15, 10, 8, 6, 4, 3]     // #vote_for
    ];
    
    const data = [{
        z: zValues,
        x: intensities,
        y: projects,
        type: 'heatmap',
        colorscale: 'Viridis',
        showscale: true,
        colorbar: {
            title: '投票数',
            titleside: 'right'
        }
    }];
    
    const layout = {
        title: '投票強度の分布ヒートマップ',
        xaxis: {
            title: '投票強度 (1-9)'
        },
        yaxis: {
            title: 'プロジェクト名'
        },
        margin: {
            l: 150,
            r: 50,
            b: 80,
            t: 80,
            pad: 4
        }
    };
    
    Plotly.newPlot(chartContainer, data, layout, {responsive: true});
}

function createPreferenceComparisonChart() {
    const chartContainer = document.getElementById('preference-comparison-chart');
    
    const projects = [
        'Chiba Youth Center PRISM',
        'Awaji Island Quest College',
        'Bio Rice Field Project',
        'Para Travel Support Team',
        'Inatori Art Center Plan',
        'JINEN TRAVEL',
        '#vote_for Project'
    ];
    
    const weakPreference = [120, 130, 110, 100, 90, 85, 95];
    const mediumPreference = [150, 140, 130, 120, 110, 105, 100];
    const strongPreference = [180, 140, 130, 120, 100, 90, 80];
    const opovVotes = [35, 30, 25, 20, 15, 15, 10];
    
    const trace1 = {
        x: projects,
        y: weakPreference,
        name: '弱い選好 (1-3)',
        type: 'bar',
        marker: {
            color: '#3498db',
            opacity: 0.7
        }
    };
    
    const trace2 = {
        x: projects,
        y: mediumPreference,
        name: '中程度の選好 (4-6)',
        type: 'bar',
        marker: {
            color: '#2ecc71',
            opacity: 0.7
        }
    };
    
    const trace3 = {
        x: projects,
        y: strongPreference,
        name: '強い選好 (7-9)',
        type: 'bar',
        marker: {
            color: '#e74c3c',
            opacity: 0.7
        }
    };
    
    const trace4 = {
        x: projects,
        y: opovVotes,
        name: '一人一票方式',
        type: 'bar',
        marker: {
            color: '#9b59b6',
            opacity: 0.7
        }
    };
    
    const data = [trace1, trace2, trace3, trace4];
    
    const layout = {
        title: 'QV方式の選好強度と一人一票方式の比較',
        barmode: 'group',
        xaxis: {
            title: 'プロジェクト名',
            tickangle: -45
        },
        yaxis: {
            title: '得票数'
        },
        margin: {
            l: 50,
            r: 50,
            b: 150,
            t: 80,
            pad: 4
        },
        legend: {
            x: 0.1,
            y: 1.1,
            orientation: 'h'
        }
    };
    
    Plotly.newPlot(chartContainer, data, layout, {responsive: true});
}

function createBudgetAllocationChart() {
    const chartContainer = document.getElementById('budget-allocation-chart');
    
    const projects = [
        'Chiba Youth Center PRISM',
        'Awaji Island Quest College',
        'Bio Rice Field Project',
        'Para Travel Support Team',
        'Inatori Art Center Plan',
        'JINEN TRAVEL',
        '#vote_for Project'
    ];
    
    const qvBudget = [44347, 39978, 38583, 34678, 31331, 30681, 30402];
    const opovBudget = [62500, 50000, 45000, 35000, 25000, 20000, 12500];
    
    const trace1 = {
        x: projects,
        y: qvBudget,
        name: 'QV方式',
        type: 'bar',
        marker: {
            color: '#3498db'
        }
    };
    
    const trace2 = {
        x: projects,
        y: opovBudget,
        name: '一人一票方式',
        type: 'bar',
        marker: {
            color: '#e74c3c'
        }
    };
    
    const data = [trace1, trace2];
    
    const layout = {
        title: '投票方式による予算配分の比較',
        barmode: 'group',
        xaxis: {
            title: 'プロジェクト名',
            tickangle: -45
        },
        yaxis: {
            title: '予算配分額 (円)'
        },
        margin: {
            l: 50,
            r: 50,
            b: 150,
            t: 80,
            pad: 4
        },
        legend: {
            x: 0.1,
            y: 1.1,
            orientation: 'h'
        }
    };
    
    Plotly.newPlot(chartContainer, data, layout, {responsive: true});
}

function createGiniCoefficientChart() {
    const chartContainer = document.getElementById('gini-coefficient-chart');
    
    const methods = ['QV方式', '一人一票方式'];
    const giniCoefficients = [0.0774, 0.2013];
    
    const data = [{
        x: methods,
        y: giniCoefficients,
        type: 'bar',
        marker: {
            color: ['#3498db', '#e74c3c'],
            opacity: 0.8
        }
    }];
    
    const layout = {
        title: 'ジニ係数の比較（値が低いほど平等）',
        xaxis: {
            title: '投票方式'
        },
        yaxis: {
            title: 'ジニ係数',
            range: [0, 0.25]
        },
        annotations: [
            {
                x: 'QV方式',
                y: 0.0774,
                text: '0.0774',
                showarrow: false,
                yshift: 10
            },
            {
                x: '一人一票方式',
                y: 0.2013,
                text: '0.2013',
                showarrow: false,
                yshift: 10
            }
        ]
    };
    
    Plotly.newPlot(chartContainer, data, layout, {responsive: true});
}

function createLorenzCurveChart() {
    const chartContainer = document.getElementById('lorenz-curve-chart');
    
    const perfectEquality = [0, 0.14, 0.29, 0.43, 0.57, 0.71, 0.86, 1];
    const qvCurve = [0, 0.12, 0.25, 0.38, 0.52, 0.67, 0.83, 1];
    const opovCurve = [0, 0.05, 0.10, 0.18, 0.28, 0.42, 0.65, 1];
    const cumulativePopulation = [0, 0.14, 0.29, 0.43, 0.57, 0.71, 0.86, 1];
    
    const trace1 = {
        x: cumulativePopulation,
        y: perfectEquality,
        name: '完全平等線',
        type: 'scatter',
        mode: 'lines',
        line: {
            color: '#2ecc71',
            width: 2,
            dash: 'dash'
        }
    };
    
    const trace2 = {
        x: cumulativePopulation,
        y: qvCurve,
        name: 'QV方式',
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: '#3498db',
            width: 2
        },
        marker: {
            size: 8
        }
    };
    
    const trace3 = {
        x: cumulativePopulation,
        y: opovCurve,
        name: '一人一票方式',
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: '#e74c3c',
            width: 2
        },
        marker: {
            size: 8
        }
    };
    
    const data = [trace1, trace2, trace3];
    
    const layout = {
        title: 'ローレンツ曲線による不平等度の比較',
        xaxis: {
            title: 'プロジェクトの累積割合',
            range: [0, 1]
        },
        yaxis: {
            title: '予算の累積割合',
            range: [0, 1]
        },
        legend: {
            x: 0.1,
            y: 0.9
        },
        shapes: [{
            type: 'line',
            x0: 0,
            y0: 0,
            x1: 1,
            y1: 1,
            line: {
                color: 'rgba(0, 0, 0, 0.2)',
                width: 1,
                dash: 'dot'
            }
        }]
    };
    
    Plotly.newPlot(chartContainer, data, layout, {responsive: true});
}

function createPercentageComparisonChart() {
    const chartContainer = document.getElementById('percentage-comparison-chart');
    
    const projects = [
        'Chiba Youth Center PRISM',
        'Awaji Island Quest College',
        'Bio Rice Field Project',
        'Para Travel Support Team',
        'Inatori Art Center Plan',
        'JINEN TRAVEL',
        '#vote_for Project'
    ];
    
    const qvPercentage = [17.7, 16.0, 15.4, 13.9, 12.5, 12.3, 12.2];
    const opovPercentage = [25.0, 20.0, 18.0, 14.0, 10.0, 8.0, 5.0];
    
    const trace1 = {
        x: projects,
        y: qvPercentage,
        name: 'QV方式',
        type: 'bar',
        marker: {
            color: '#3498db'
        },
        text: qvPercentage.map(val => val.toFixed(1) + '%'),
        textposition: 'auto'
    };
    
    const trace2 = {
        x: projects,
        y: opovPercentage,
        name: '一人一票方式',
        type: 'bar',
        marker: {
            color: '#e74c3c'
        },
        text: opovPercentage.map(val => val.toFixed(1) + '%'),
        textposition: 'auto'
    };
    
    const data = [trace1, trace2];
    
    const layout = {
        title: '予算配分比率の比較（%）',
        barmode: 'group',
        xaxis: {
            title: 'プロジェクト名',
            tickangle: -45
        },
        yaxis: {
            title: '予算配分比率 (%)',
            range: [0, 30]
        },
        margin: {
            l: 50,
            r: 50,
            b: 150,
            t: 80,
            pad: 4
        },
        legend: {
            x: 0.1,
            y: 1.1,
            orientation: 'h'
        }
    };
    
    Plotly.newPlot(chartContainer, data, layout, {responsive: true});
}

function createVoteComparisonChart() {
    const chartContainer = document.getElementById('vote-comparison-chart');
    
    const projects = [
        'Chiba Youth Center PRISM',
        'Awaji Island Quest College',
        'Bio Rice Field Project',
        'Para Travel Support Team',
        'Inatori Art Center Plan',
        'JINEN TRAVEL',
        '#vote_for Project'
    ];
    
    const qvVotes = [477, 430, 415, 373, 337, 330, 327];
    const opovVotes = [35, 30, 25, 20, 15, 15, 10];
    
    const trace1 = {
        x: projects,
        y: qvVotes,
        name: 'QV方式',
        type: 'bar',
        marker: {
            color: '#3498db'
        }
    };
    
    const trace2 = {
        x: projects,
        y: opovVotes,
        name: '一人一票方式',
        type: 'bar',
        marker: {
            color: '#e74c3c'
        }
    };
    
    const data = [trace1, trace2];
    
    const layout = {
        title: '投票方式による得票数の比較',
        barmode: 'group',
        xaxis: {
            title: 'プロジェクト名',
            tickangle: -45
        },
        yaxis: {
            title: '得票数'
        },
        margin: {
            l: 50,
            r: 50,
            b: 150,
            t: 80,
            pad: 4
        },
        legend: {
            x: 0.1,
            y: 1.1,
            orientation: 'h'
        }
    };
    
    Plotly.newPlot(chartContainer, data, layout, {responsive: true});
}
