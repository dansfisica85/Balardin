// Sistema de Análise de Desempenho Acadêmico - GitHub Pages Version

class SistemaAnalise {
    constructor() {
        this.serieSelect = document.getElementById('serieSelect');
        this.alunoSelect = document.getElementById('alunoSelect');
        this.buscarBtn = document.getElementById('buscarAluno');
        this.resultadoAluno = document.getElementById('resultadoAluno');
        this.dadosAluno = document.getElementById('dadosAluno');
        this.relatorioNotas = document.getElementById('relatorioNotas');
        this.relatorioFrequencia = document.getElementById('relatorioFrequencia');
        this.relatorioCombinado = document.getElementById('relatorioCombinado');
        this.resultadoRelatorios = document.getElementById('resultadoRelatorios');
        this.conteudoRelatorio = document.getElementById('conteudoRelatorio');
        this.tituloRelatorio = document.getElementById('tituloRelatorio');
        this.loading = document.getElementById('loading');
        this.seriesResumoContainer = document.getElementById('seriesResumo');
        this.serieRelatorioSelect = document.getElementById('serieRelatorio');
        this.arquivoSelect = document.getElementById('arquivoSelect');
        
        // Dados carregados do JSON estático
        this.dadosAlunos = null;
        
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.loadSeries();
        this.loadSeriesResumo();
        this.loadTurmasRelatorio();
        this.loadArquivos();
        this.setupEventListeners();
    }
    
    async loadData() {
        try {
            this.showLoading();
            const response = await fetch('data/alunos_compilado.json');
            this.dadosAlunos = await response.json();
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
            alert('Erro ao carregar dados dos alunos. Verifique se o arquivo data/alunos_compilado.json existe.');
        } finally {
            this.hideLoading();
        }
    }
    
    setupEventListeners() {
        // Mudança de série
        this.serieSelect.addEventListener('change', () => {
            const serie = this.serieSelect.value;
            if (serie) {
                this.loadAlunos(serie);
            } else {
                this.alunoSelect.innerHTML = '<option value="">Primeiro selecione uma série...</option>';
                this.alunoSelect.disabled = true;
                this.buscarBtn.disabled = true;
            }
        });
        
        // Mudança de aluno
        this.alunoSelect.addEventListener('change', () => {
            this.buscarBtn.disabled = !this.alunoSelect.value;
        });
        
        // Mudança de arquivo
        this.arquivoSelect.addEventListener('change', () => {
            const arquivo = this.arquivoSelect.value;
            if (arquivo) {
                this.showTurmaInfo(arquivo);
            }
        });
        
        // Buscar dados do aluno
        this.buscarBtn.addEventListener('click', () => {
            const serie = this.serieSelect.value;
            const aluno = this.alunoSelect.value;
            if (serie && aluno) {
                this.loadDadosAluno(serie, aluno);
            }
        });
        
        // Relatórios
        this.relatorioNotas.addEventListener('click', () => {
            this.loadRelatorioNotasBaixas();
        });
        
        this.relatorioFrequencia.addEventListener('click', () => {
            this.loadRelatorioFrequenciaBaixa();
        });
        
        this.relatorioCombinado.addEventListener('click', () => {
            this.loadRelatorioCombinado();
        });
        
        // Event listener para seleção de turma no relatório
        this.serieRelatorioSelect.addEventListener('change', () => {
            const turma = this.serieRelatorioSelect.value;
            if (turma) {
                this.showRelatorioTurma(turma);
            }
        });
    }
    
    showLoading() {
        this.loading.style.display = 'flex';
    }
    
    hideLoading() {
        this.loading.style.display = 'none';
    }
    
    loadSeries() {
        if (!this.dadosAlunos) return;
        
        const series = Object.keys(this.dadosAlunos);
        this.serieSelect.innerHTML = '<option value="">Selecione uma série...</option>';
        series.forEach(serie => {
            const option = document.createElement('option');
            option.value = serie;
            option.textContent = serie;
            this.serieSelect.appendChild(option);
        });
    }
    
    loadArquivos() {
        if (!this.dadosAlunos) return;
        
        const arquivos = new Set();
        Object.values(this.dadosAlunos).forEach(serieData => {
            Object.values(serieData).forEach(aluno => {
                if (aluno.arquivo_origem) {
                    const arquivo = aluno.arquivo_origem.replace('.pdf', '');
                    arquivos.add(arquivo);
                }
            });
        });
        
        this.arquivoSelect.innerHTML = '<option value="">Selecione...</option>';
        Array.from(arquivos).sort().forEach(arquivo => {
            const option = document.createElement('option');
            option.value = arquivo;
            option.textContent = arquivo;
            this.arquivoSelect.appendChild(option);
        });
    }
    
    loadSeriesResumo() {
        if (!this.dadosAlunos) return;
        
        let html = '';
        Object.entries(this.dadosAlunos).forEach(([serie, alunos]) => {
            const totalAlunos = Object.keys(alunos).length;
            const frequencias = Object.values(alunos).map(a => a.frequencia_media || 0);
            const freqMedia = frequencias.length > 0 ? 
                (frequencias.reduce((a, b) => a + b, 0) / frequencias.length).toFixed(1) : 0;
            
            html += `
                <div class="serie-resumo-card fade-in">
                    <h4>${serie}</h4>
                    <p><strong>Alunos:</strong> ${totalAlunos}</p>
                    <p><strong>Freq. Média:</strong> ${freqMedia}%</p>
                </div>`;
        });
        this.seriesResumoContainer.innerHTML = html;
    }
    
    loadTurmasRelatorio() {
        const turmas = [
            '1A', '1B', '1C', '1D', '1E',
            '2A', '2B', '2C', '2D', '2E', '2F',
            '3A', '3B', '3C', '3D', '3E', '3F', '3G',
            '6A', '6B',
            '7A', '7B', '7C',
            '8A', '8B', '8C',
            '9A', '9B'
        ];
        
        this.serieRelatorioSelect.innerHTML = '<option value="">Selecione...</option>';
        turmas.forEach(turma => {
            const option = document.createElement('option');
            option.value = turma;
            option.textContent = turma;
            this.serieRelatorioSelect.appendChild(option);
        });
    }
    
    loadAlunos(serie) {
        if (!this.dadosAlunos || !this.dadosAlunos[serie]) return;
        
        const alunos = Object.keys(this.dadosAlunos[serie]);
        this.alunoSelect.innerHTML = '<option value="">Selecione um aluno...</option>';
        alunos.sort().forEach(aluno => {
            const option = document.createElement('option');
            option.value = aluno;
            option.textContent = aluno;
            this.alunoSelect.appendChild(option);
        });
        
        this.alunoSelect.disabled = false;
    }
    
    loadDadosAluno(serie, nomeAluno) {
        if (!this.dadosAlunos || !this.dadosAlunos[serie] || !this.dadosAlunos[serie][nomeAluno]) {
            alert('Dados do aluno não encontrados');
            return;
        }
        
        const aluno = this.dadosAlunos[serie][nomeAluno];
        this.showDadosAluno(aluno);
    }
    
    showDadosAluno(aluno) {
        let html = `
            <div class="student-info">
                <h3>${aluno.nome}</h3>
                <p><strong>RA:</strong> ${aluno.ra}</p>
                <p><strong>Série:</strong> ${aluno.serie}</p>
                <p><strong>Turma:</strong> ${aluno.turma}</p>
                <p><strong>Frequência Média:</strong> ${aluno.frequencia_media}%</p>
                <p><strong>Total de Faltas:</strong> ${aluno.total_faltas}</p>
            </div>
        `;
        
        if (aluno.disciplinas && aluno.disciplinas.length > 0) {
            html += '<div class="disciplinas-grid">';
            aluno.disciplinas.forEach(disciplina => {
                const problema = disciplina.media_semestral < 5 || disciplina.freq_semestral < 75;
                html += `
                    <div class="disciplina-card ${problema ? 'problema' : ''}">
                        <h4>${disciplina.nome}</h4>
                        <div class="notas-info">
                            <div class="nota-item ${disciplina.media_semestral < 5 ? 'media-baixa' : ''}">
                                Média: ${disciplina.media_semestral}
                            </div>
                            <div class="freq-item ${disciplina.freq_semestral < 75 ? (disciplina.freq_semestral < 60 ? 'freq-muito-baixa' : 'freq-baixa') : ''}">
                                Freq: ${disciplina.freq_semestral}%
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        this.dadosAluno.innerHTML = html;
        this.resultadoAluno.style.display = 'block';
        this.resultadoAluno.scrollIntoView({ behavior: 'smooth' });
    }
    
    showTurmaInfo(arquivo) {
        if (!this.dadosAlunos) return;
        
        const alunos = [];
        Object.values(this.dadosAlunos).forEach(serieData => {
            Object.values(serieData).forEach(aluno => {
                if (aluno.arquivo_origem && aluno.arquivo_origem.replace('.pdf', '') === arquivo) {
                    alunos.push(aluno);
                }
            });
        });
        
        this.showRelatorioTurmaDetalhado(arquivo, alunos);
    }
    
    showRelatorioTurma(turma) {
        this.showTurmaInfo(turma);
    }
    
    showRelatorioTurmaDetalhado(codigo, alunos) {
        let html = `
            <div class="relatorio-section">
                <h3>📋 Relatório da Turma ${codigo}</h3>
                <p><strong>Total de alunos:</strong> ${alunos.length}</p>
        `;
        
        if (alunos.length > 0) {
            const freqMedia = (alunos.reduce((sum, a) => sum + (a.frequencia_media || 0), 0) / alunos.length).toFixed(1);
            const totalFaltas = alunos.reduce((sum, a) => sum + (a.total_faltas || 0), 0);
            
            html += `
                <p><strong>Frequência média da turma:</strong> ${freqMedia}%</p>
                <p><strong>Total de faltas da turma:</strong> ${totalFaltas}</p>
                <div class="alunos-lista">
            `;
            
            alunos.sort((a, b) => a.nome.localeCompare(b.nome)).forEach(aluno => {
                const risco = aluno.frequencia_media < 75 ? 'risco-evasao' : '';
                html += `
                    <div class="estudante-item ${risco}">
                        <h4>${aluno.nome}</h4>
                        <p><strong>RA:</strong> ${aluno.ra}</p>
                        <p><strong>Frequência:</strong> ${aluno.frequencia_media}%</p>
                        <p><strong>Faltas:</strong> ${aluno.total_faltas}</p>
                    </div>
                `;
            });
            
            html += '</div>';
        }
        
        html += '</div>';
        
        this.tituloRelatorio.innerHTML = `<i class="fas fa-file-alt"></i> Relatório da Turma ${codigo}`;
        this.conteudoRelatorio.innerHTML = html;
        this.resultadoRelatorios.style.display = 'block';
        this.resultadoRelatorios.scrollIntoView({ behavior: 'smooth' });
    }
    
    loadRelatorioNotasBaixas() {
        if (!this.dadosAlunos) return;
        
        const alunosNotasBaixas = [];
        Object.values(this.dadosAlunos).forEach(serieData => {
            Object.values(serieData).forEach(aluno => {
                if (aluno.disciplinas) {
                    const disciplinasProblema = aluno.disciplinas.filter(d => d.media_semestral < 5);
                    if (disciplinasProblema.length > 0) {
                        alunosNotasBaixas.push({
                            ...aluno,
                            disciplinas_problema: disciplinasProblema
                        });
                    }
                }
            });
        });
        
        this.showRelatorioNotasBaixas(alunosNotasBaixas);
    }
    
    showRelatorioNotasBaixas(alunos) {
        let html = `
            <div class="relatorio-section">
                <h3>⚠️ Relatório de Notas Baixas (< 5.0)</h3>
                <p><strong>Total de alunos com notas baixas:</strong> ${alunos.length}</p>
                <div class="alunos-lista">
        `;
        
        alunos.forEach(aluno => {
            html += `
                <div class="estudante-item risco-reprovacao">
                    <h4>${aluno.nome} - ${aluno.serie}</h4>
                    <div class="disciplinas-problema">
            `;
            aluno.disciplinas_problema.forEach(d => {
                html += `<div class="disciplina-problema">📘 ${d.nome}: média ${d.media_semestral}</div>`;
            });
            html += `
                    </div>
                </div>
            `;
        });
        
        html += '</div></div>';
        
        this.tituloRelatorio.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Relatório de Notas Baixas';
        this.conteudoRelatorio.innerHTML = html;
        this.resultadoRelatorios.style.display = 'block';
        this.resultadoRelatorios.scrollIntoView({ behavior: 'smooth' });
    }
    
    loadRelatorioFrequenciaBaixa() {
        if (!this.dadosAlunos) return;
        
        const alunosFreqBaixa = [];
        Object.values(this.dadosAlunos).forEach(serieData => {
            Object.values(serieData).forEach(aluno => {
                if (aluno.frequencia_media < 75) {
                    alunosFreqBaixa.push(aluno);
                }
            });
        });
        
        this.showRelatorioFrequenciaBaixa(alunosFreqBaixa);
    }
    
    showRelatorioFrequenciaBaixa(alunos) {
        let html = `
            <div class="relatorio-section">
                <h3>🕒 Relatório de Frequência Baixa (< 75%)</h3>
                <p><strong>Total de alunos com frequência baixa:</strong> ${alunos.length}</p>
                <div class="alunos-lista">
        `;
        
        alunos.sort((a, b) => a.frequencia_media - b.frequencia_media).forEach(aluno => {
            const riscoAlto = aluno.frequencia_media < 60;
            html += `
                <div class="estudante-item ${riscoAlto ? 'risco-evasao' : ''}">
                    <h4>${aluno.nome} - ${aluno.serie}</h4>
                    <p><strong>Frequência:</strong> ${aluno.frequencia_media}%</p>
                    <p><strong>Total de faltas:</strong> ${aluno.total_faltas}</p>
                </div>
            `;
        });
        
        html += '</div></div>';
        
        this.tituloRelatorio.innerHTML = '<i class="fas fa-user-clock"></i> Relatório de Frequência Baixa';
        this.conteudoRelatorio.innerHTML = html;
        this.resultadoRelatorios.style.display = 'block';
        this.resultadoRelatorios.scrollIntoView({ behavior: 'smooth' });
    }
    
    loadRelatorioCombinado() {
        this.tituloRelatorio.innerHTML = '<i class="fas fa-layer-group"></i> Relatório Combinado';
        
        let html = '<div class="relatorio-section">';
        html += '<h3>📊 Relatório Combinado - Notas e Frequência</h3>';
        
        if (!this.dadosAlunos) {
            html += '<p>Dados não carregados.</p></div>';
            this.conteudoRelatorio.innerHTML = html;
            this.resultadoRelatorios.style.display = 'block';
            return;
        }
        
        Object.entries(this.dadosAlunos).forEach(([serie, alunos]) => {
            html += `<div class="serie-relatorio"><h4>📚 ${serie}</h4><div class="estudantes-grid">`;
            
            Object.values(alunos).forEach(aluno => {
                const freqBaixa = aluno.frequencia_media < 75;
                const notasBaixas = aluno.disciplinas ? 
                    aluno.disciplinas.filter(d => d.media_semestral < 5).length : 0;
                
                if (freqBaixa || notasBaixas > 0) {
                    html += `
                        <div class="estudante-item ${freqBaixa ? 'risco-evasao' : ''} ${notasBaixas > 0 ? 'risco-reprovacao' : ''}">
                            <h4>${aluno.nome}</h4>
                            <p><strong>Frequência:</strong> ${aluno.frequencia_media}%</p>
                            <p><strong>Disciplinas com nota <5:</strong> ${notasBaixas}</p>
                        </div>`;
                }
            });
            
            html += '</div></div>';
        });
        
        html += '</div>';
        
        this.conteudoRelatorio.innerHTML = html;
        this.resultadoRelatorios.style.display = 'block';
        this.resultadoRelatorios.scrollIntoView({ behavior: 'smooth' });
    }
}

// Inicializar sistema quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    new SistemaAnalise();
});
