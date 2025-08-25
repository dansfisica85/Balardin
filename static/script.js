// Sistema de Análise de Desempenho Acadêmico - JavaScript

class SistemaAnalise {
    constructor() {
        this.serieSelect = document.getElementById('serieSelect');
        this.alunoSelect = document.getElementById('alunoSelect');
        this.buscarBtn = document.getElementById('buscarAluno');
        this.resultadoAluno = document.getElementById('resultadoAluno');
        this.dadosAluno = document.getElementById('dadosAluno');
        this.relatorioNotas = document.getElementById('relatorioNotas');
        this.relatorioFrequencia = document.getElementById('relatorioFrequencia');
        this.resultadoRelatorios = document.getElementById('resultadoRelatorios');
        this.conteudoRelatorio = document.getElementById('conteudoRelatorio');
        this.tituloRelatorio = document.getElementById('tituloRelatorio');
        this.reprocessarBtn = document.getElementById('reprocessar');
        this.loading = document.getElementById('loading');
        
        this.init();
    }
    
    init() {
        this.loadSeries();
        this.setupEventListeners();
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
        
        // Reprocessar PDFs
        this.reprocessarBtn.addEventListener('click', () => {
            this.reprocessarPDFs();
        });
    }
    
    showLoading() {
        this.loading.style.display = 'flex';
    }
    
    hideLoading() {
        this.loading.style.display = 'none';
    }
    
    async apiCall(url) {
        this.showLoading();
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.status === 'error') {
                throw new Error(data.message);
            }
            
            return data.data;
        } catch (error) {
            console.error('Erro na API:', error);
            alert('Erro: ' + error.message);
            throw error;
        } finally {
            this.hideLoading();
        }
    }
    
    async loadSeries() {
        try {
            const series = await this.apiCall('/api/series');
            
            this.serieSelect.innerHTML = '<option value="">Selecione uma série...</option>';
            series.forEach(serie => {
                const option = document.createElement('option');
                option.value = serie;
                option.textContent = serie;
                this.serieSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Erro ao carregar séries:', error);
        }
    }
    
    async loadAlunos(serie) {
        try {
            const alunos = await this.apiCall(`/api/alunos/${encodeURIComponent(serie)}`);
            
            this.alunoSelect.innerHTML = '<option value="">Selecione um aluno...</option>';
            alunos.forEach(aluno => {
                const option = document.createElement('option');
                option.value = aluno;
                option.textContent = aluno;
                this.alunoSelect.appendChild(option);
            });
            
            this.alunoSelect.disabled = false;
        } catch (error) {
            console.error('Erro ao carregar alunos:', error);
            this.alunoSelect.innerHTML = '<option value="">Erro ao carregar alunos</option>';
        }
    }
    
    async loadDadosAluno(serie, aluno) {
        try {
            const dados = await this.apiCall(`/api/aluno/${encodeURIComponent(serie)}/${encodeURIComponent(aluno)}`);
            this.displayDadosAluno(dados);
        } catch (error) {
            console.error('Erro ao carregar dados do aluno:', error);
        }
    }
    
    displayDadosAluno(dados) {
        const { aluno, alertas, risco_reprovacao, risco_evasao } = dados;
        
        let html = `
            <div class="student-info fade-in">
                <h3><i class="fas fa-user"></i> ${aluno.nome}</h3>
                <p><strong>Série:</strong> ${aluno.serie}</p>
                <p><strong>Frequência Média:</strong> ${aluno.frequencia_media}%</p>
                <p><strong>Arquivo:</strong> ${aluno.arquivo_origem}</p>
            </div>
        `;
        
        // Alertas
        if (alertas.length > 0) {
            html += '<div class="alertas">';
            alertas.forEach(alerta => {
                const classe = alerta.tipo === 'evasao' ? 'evasao' : 'reprovacao';
                const icone = alerta.tipo === 'evasao' ? 'fas fa-exclamation-triangle' : 'fas fa-times-circle';
                html += `
                    <div class="alerta ${classe}">
                        <i class="${icone}"></i>
                        ${alerta.message}
                    </div>
                `;
            });
            html += '</div>';
        }
        
        // Disciplinas
        html += '<h4><i class="fas fa-book"></i> Disciplinas e Notas</h4>';
        html += '<div class="disciplinas-grid">';
        
        aluno.disciplinas.forEach(disciplina => {
            const isProblema = disciplina.media_semestral < 5;
            html += `
                <div class="disciplina-card ${isProblema ? 'problema' : ''}">
                    <h4>${disciplina.nome}</h4>
                    <div class="notas-info">
                        <div class="nota-item">
                            <strong>1º Bim</strong><br>
                            ${disciplina.nota_1bim}
                        </div>
                        <div class="nota-item">
                            <strong>2º Bim</strong><br>
                            ${disciplina.nota_2bim}
                        </div>
                        <div class="nota-item ${isProblema ? 'media-baixa' : ''}">
                            <strong>Média</strong><br>
                            ${disciplina.media_semestral}
                            ${isProblema ? ' <i class="fas fa-exclamation-triangle"></i>' : ''}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        
        this.dadosAluno.innerHTML = html;
        this.resultadoAluno.style.display = 'block';
        this.resultadoAluno.scrollIntoView({ behavior: 'smooth' });
    }
    
    async loadRelatorioNotasBaixas() {
        try {
            const relatorio = await this.apiCall('/api/relatorio/notas-baixas');
            this.displayRelatorio('Relatório de Notas Baixas (< 5.0)', relatorio, 'notas');
        } catch (error) {
            console.error('Erro ao carregar relatório de notas baixas:', error);
        }
    }
    
    async loadRelatorioFrequenciaBaixa() {
        try {
            const relatorio = await this.apiCall('/api/relatorio/frequencia-baixa');
            this.displayRelatorio('Relatório de Frequência Baixa (< 75%)', relatorio, 'frequencia');
        } catch (error) {
            console.error('Erro ao carregar relatório de frequência baixa:', error);
        }
    }
    
    displayRelatorio(titulo, dados, tipo) {
        this.tituloRelatorio.innerHTML = `<i class="fas fa-file-alt"></i> ${titulo}`;
        
        if (Object.keys(dados).length === 0) {
            this.conteudoRelatorio.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-check-circle" style="font-size: 3em; color: #27ae60; margin-bottom: 20px;"></i>
                    <h3>Excelente! Nenhum problema encontrado.</h3>
                    <p>Todos os estudantes estão com ${tipo === 'notas' ? 'notas adequadas' : 'frequência adequada'}.</p>
                </div>
            `;
        } else {
            let html = '';
            
            Object.entries(dados).forEach(([serie, estudantes]) => {
                html += `
                    <div class="serie-section fade-in">
                        <h3><i class="fas fa-users"></i> ${serie} - ${estudantes.length} estudante(s) com problema</h3>
                        <div class="estudantes-lista">
                `;
                
                estudantes.forEach(estudante => {
                    if (tipo === 'notas') {
                        html += `
                            <div class="estudante-item">
                                <div class="estudante-nome">
                                    <i class="fas fa-user"></i> ${estudante.nome}
                                </div>
                                <p><strong>Total de disciplinas com problema:</strong> ${estudante.total_disciplinas_problema}</p>
                                <div class="disciplinas-problema">
                        `;
                        
                        estudante.disciplinas_problema.forEach(disc => {
                            html += `
                                <div class="disciplina-problema">
                                    <strong>${disc.disciplina}:</strong> Média ${disc.media} 
                                    (1º Bim: ${disc.nota_1bim}, 2º Bim: ${disc.nota_2bim})
                                </div>
                            `;
                        });
                        
                        html += '</div></div>';
                    } else {
                        const riscoClasse = estudante.risco_nivel === 'ALTO' ? 'risco-alto' : 'risco-medio';
                        html += `
                            <div class="estudante-item ${riscoClasse}">
                                <div class="estudante-nome">
                                    <i class="fas fa-user"></i> ${estudante.nome}
                                </div>
                                <p><strong>Frequência:</strong> ${estudante.frequencia}%</p>
                                <p><strong>Nível de Risco:</strong> 
                                    <span style="color: ${estudante.risco_nivel === 'ALTO' ? '#dc3545' : '#ffc107'};">
                                        ${estudante.risco_nivel}
                                    </span>
                                </p>
                            </div>
                        `;
                    }
                });
                
                html += '</div></div>';
            });
            
            this.conteudoRelatorio.innerHTML = html;
        }
        
        this.resultadoRelatorios.style.display = 'block';
        this.resultadoRelatorios.scrollIntoView({ behavior: 'smooth' });
    }
    
    async reprocessarPDFs() {
        if (confirm('Tem certeza que deseja reprocessar todos os PDFs? Esta operação pode demorar alguns minutos.')) {
            try {
                await this.apiCall('/api/reprocessar');
                alert('PDFs reprocessados com sucesso!');
                
                // Recarregar as séries
                await this.loadSeries();
                
                // Limpar seleções
                this.alunoSelect.innerHTML = '<option value="">Primeiro selecione uma série...</option>';
                this.alunoSelect.disabled = true;
                this.buscarBtn.disabled = true;
                
                // Ocultar resultados
                this.resultadoAluno.style.display = 'none';
                this.resultadoRelatorios.style.display = 'none';
                
            } catch (error) {
                console.error('Erro ao reprocessar PDFs:', error);
            }
        }
    }
}

// Inicializar sistema quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    new SistemaAnalise();
});
