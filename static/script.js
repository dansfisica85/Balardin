// Sistema de Análise de Desempenho Acadêmico - JavaScript

class SistemaAnalise {
    constructor() {
        this.serieSelect = document.getElementById('serieSelect');
        this.alunoSelect = document.getElementById('alunoSelect');
    this.arquivoSelect = document.getElementById('arquivoSelect');
    this.serieRelatorio = document.getElementById('serieRelatorio');
        this.buscarBtn = document.getElementById('buscarAluno');
        this.resultadoAluno = document.getElementById('resultadoAluno');
        this.dadosAluno = document.getElementById('dadosAluno');
        this.relatorioNotas = document.getElementById('relatorioNotas');
        this.relatorioFrequencia = document.getElementById('relatorioFrequencia');
    this.relatorioCombinado = document.getElementById('relatorioCombinado');
        this.resultadoRelatorios = document.getElementById('resultadoRelatorios');
        this.conteudoRelatorio = document.getElementById('conteudoRelatorio');
        this.tituloRelatorio = document.getElementById('tituloRelatorio');
        this.reprocessarBtn = document.getElementById('reprocessar');
        this.loading = document.getElementById('loading');
    this.seriesResumoContainer = document.getElementById('seriesResumo');
        this.serieRelatorioSelect = document.getElementById('serieRelatorio');
        
        this.init();
    }
    
    init() {
        this.loadSeries();
    this.loadArquivos();
    this.loadSeriesResumo();
        this.loadTurmasRelatorio();
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

        // Mudança de arquivo (turma)
        this.arquivoSelect.addEventListener('change', ()=>{
            const codigo = this.arquivoSelect.value;
            if (codigo) {
                this.loadTurma(codigo);
            } else {
                this.resultadoAluno.style.display = 'none';
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
        this.relatorioCombinado.addEventListener('click', () => {
            this.loadRelatorioCombinado();
        });
        
        // Event listener para seleção de turma no relatório
        this.serieRelatorioSelect.addEventListener('change', () => {
            const turma = this.serieRelatorioSelect.value;
            if (turma) {
                console.log('Turma selecionada:', turma);
                // Aqui você pode adicionar funcionalidade específica para quando uma turma é selecionada
                // Por exemplo: this.loadRelatorioTurma(turma);
            }
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
            
            // Verificar se a resposta é HTML (erro comum no Netlify)
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('text/html')) {
                throw new Error('Servidor retornou HTML em vez de JSON. Verifique a configuração do Netlify.');
            }
            
            const data = await response.json();
            
            if (data.status === 'error') {
                throw new Error(data.message);
            }
            
            return data.data;
        } catch (error) {
            console.error('Erro na API:', error);
            
            // Fallback para dados hardcoded se a API falhar
            if (url.includes('/api/turmas')) {
                console.log('Usando fallback para turmas');
                return ["1A", "1B", "1C", "1D", "1E", "2A", "2B", "2C", "2D", "2E", "2F", "3A", "3B", "3C", "3D", "3E", "3F", "3G", "6A", "6B", "7A", "7B", "7C", "8A", "8B", "8C", "9A", "9B"];
            }
            
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

    async loadArquivos() {
        try {
            const arquivos = await this.apiCall('/api/turmas');
            this.arquivoSelect.innerHTML = '<option value="">Selecione...</option>';
            if (this.serieRelatorio) this.serieRelatorio.innerHTML = '<option value="">Selecione...</option>';
            arquivos.forEach(arq=>{
                const opt = document.createElement('option');
                opt.value = arq;
                opt.textContent = arq;
                this.arquivoSelect.appendChild(opt);
                if (this.serieRelatorio){
                    const opt2 = document.createElement('option');
                    opt2.value = arq;
                    opt2.textContent = arq;
                    this.serieRelatorio.appendChild(opt2);
                }
            });
            // Listener para select de relatório rápido
            if (this.serieRelatorio && !this._serieRelatorioBound){
                this._serieRelatorioBound = true;
                this.serieRelatorio.addEventListener('change', ()=>{
                    const cod = this.serieRelatorio.value;
                    if (cod){
                        this.loadTurma(cod);
                    } else {
                        this.resultadoAluno.style.display='none';
                    }
                });
            }
        } catch (e) {
            console.error('Erro ao carregar turmas/arquivos', e);
        }
    }

    async loadTurma(codigo){
        try {
            const alunos = await this.apiCall(`/api/turma/${encodeURIComponent(codigo)}`);
            let html = `<h3>Relatório da Turma ${codigo}</h3>`;
            if (alunos.length === 0) {
                html += '<p>Nenhum aluno encontrado.</p>';
            } else {
                // Estatísticas agregadas
                const total = alunos.length;
                const freqMed = (alunos.reduce((acc,a)=>acc+parseFloat(a.frequencia_media||0),0)/total).toFixed(1);
                html += `<p><strong>Total de alunos:</strong> ${total}</p>`;
                html += `<p><strong>Frequência média da turma:</strong> ${freqMed}%</p>`;
                
                // Estatísticas por disciplina
                const stats = {};
                alunos.forEach(a=>{
                    (a.disciplinas||[]).forEach(d=>{
                        if (!stats[d.nome]) stats[d.nome]={notas:[],freqs:[]};
                        if (d.media_semestral > 0) stats[d.nome].notas.push(d.media_semestral);
                        if (d.freq_semestral > 0) stats[d.nome].freqs.push(d.freq_semestral);
                    });
                });
                
                if (Object.keys(stats).length>0){
                    html += `<h4>Disciplinas</h4>`;
                    html += `<table class="table table-striped" style="font-size:0.9em;">`;
                    html += `<thead><tr><th>Disciplina</th><th>Média</th><th>Freq. Média</th><th>Alunos <5.0</th><th>Alunos <75%</th></tr></thead><tbody>`;
                    Object.entries(stats).forEach(([nome,vals])=>{
                        const medias = vals.notas;
                        const freqs = vals.freqs;
                        const med = medias.length ? (medias.reduce((a,b)=>a+b,0)/medias.length).toFixed(1) : '-';
                        const freq = freqs.length ? (freqs.reduce((a,b)=>a+b,0)/freqs.length).toFixed(1) : '-';
                        const abaixo5 = medias.filter(n=>n<5).length;
                        const abaixo75 = freqs.filter(f=>f<75).length;
                        html += `<tr><td>${nome}</td><td>${med}</td><td>${freq}%</td><td>${abaixo5}</td><td>${abaixo75}</td></tr>`;
                    });
                    html += '</tbody></table>';
                }
                
                // Lista de alunos com problemas
                const alunosProblema = alunos.filter(a => {
                    const temNotaBaixa = a.disciplinas.some(d => d.media_semestral > 0 && d.media_semestral < 5);
                    const temFreqBaixa = a.frequencia_media < 75 || a.disciplinas.some(d => d.freq_semestral > 0 && d.freq_semestral < 75);
                    return temNotaBaixa || temFreqBaixa;
                });
                
                if (alunosProblema.length > 0) {
                    html += `<h4>Alunos com Problemas (${alunosProblema.length})</h4>`;
                    html += '<div class="problemas-lista">';
                    alunosProblema.forEach(a => {
                        const problemas = [];
                        if (a.frequencia_media < 75) problemas.push(`Freq geral: ${a.frequencia_media}%`);
                        a.disciplinas.forEach(d => {
                            if (d.media_semestral > 0 && d.media_semestral < 5) 
                                problemas.push(`${d.nome}: nota ${d.media_semestral}`);
                            if (d.freq_semestral > 0 && d.freq_semestral < 75) 
                                problemas.push(`${d.nome}: freq ${d.freq_semestral}%`);
                        });
                        html += `<div class="aluno-problema"><strong>${a.nome}</strong>: ${problemas.join(', ')}</div>`;
                    });
                    html += '</div>';
                }
                
                // Lista completa de alunos
                html += `<h4>Todos os Alunos (${total})</h4>`;
                html += '<ul class="lista-turma">';
                alunos.forEach(a=>{
                    html += `<li>${a.nome} - ${a.serie} - Freq: ${a.frequencia_media}% - ${a.disciplinas.length} disciplinas</li>`;
                });
                html += '</ul>';
            }
            this.dadosAluno.innerHTML = html;
            this.resultadoAluno.style.display = 'block';
            this.resultadoAluno.scrollIntoView({ behavior: 'smooth' });
        } catch (e) {
            console.error('Erro ao carregar turma', e);
            alert('Erro ao carregar dados da turma: ' + e.message);
        }
    }

    async loadSeriesResumo() {
        try {
            const resumo = await this.apiCall('/api/resumo/series/simples');
            let html = '';
            Object.entries(resumo).forEach(([serie, dados]) => {
                html += `
                  <div class="serie-resumo-card fade-in">
                    <h4>${serie}</h4>
                    <p><strong>Alunos:</strong> ${dados.alunos}</p>
                    <p><strong>Freq. Média:</strong> ${dados.frequencia_media_serie}%</p>
                  </div>`;
            });
            this.seriesResumoContainer.innerHTML = html;
        } catch (e) {
            console.error('Erro ao carregar resumo séries', e);
        }
    }

    async loadTurmasRelatorio() {
        try {
            // Lista das turmas conforme especificado
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
        } catch (error) {
            console.error('Erro ao carregar turmas para relatório:', error);
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
        html += '<h4><i class="fas fa-book"></i> Disciplinas, Notas e Frequências</h4>';
        html += '<div class="disciplinas-grid">';
        
        aluno.disciplinas.forEach(disciplina => {
            const isProblema = disciplina.media_semestral < 5;
            const freqSem = disciplina.freq_semestral ?? 0;
            const freq1 = disciplina.freq_1bim ?? 0;
            const freq2 = disciplina.freq_2bim ?? 0;
            const freqClasse = (freqSem > 0 && freqSem < 60) ? 'freq-muito-baixa' : ((freqSem > 0 && freqSem < 75) ? 'freq-baixa' : '');
            html += `
                <div class="disciplina-card ${isProblema ? 'problema' : ''} ${freqClasse}">
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
                        <div class="freq-item">
                            <strong>Freq 1ºB</strong><br>
                            ${freq1 || '-'}%
                        </div>
                        <div class="freq-item">
                            <strong>Freq 2ºB</strong><br>
                            ${freq2 || '-'}%
                        </div>
                        <div class="freq-item ${freqClasse}">
                            <strong>Freq Sem</strong><br>
                            ${freqSem || '-'}%
                            ${(freqSem > 0 && freqSem < 75) ? ' <i class="fas fa-exclamation-circle"></i>' : ''}
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

    async loadRelatorioCombinado() {
        try {
            const relatorio = await this.apiCall('/api/relatorio/combinais');
            this.displayRelatorio('Relatório Combinado (Notas & Frequência)', relatorio, 'combinado');
        } catch (error) {
            console.error('Erro ao carregar relatório combinado:', error);
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
                    } else if (tipo === 'frequencia') {
                        // Novo formato: frequencia baixa inclui disciplinas_freq_baixa
                        const riscoClasse = estudante.risco_nivel === 'ALTO' ? 'risco-alto' : 'risco-medio';
                        html += `
                            <div class="estudante-item ${riscoClasse}">
                                <div class="estudante-nome">
                                    <i class="fas fa-user"></i> ${estudante.nome}
                                </div>
                                <p><strong>Frequência Média do Aluno:</strong> ${estudante.frequencia_media_aluno}%</p>
                                <p><strong>Nível de Risco:</strong> 
                                    <span style="color: ${estudante.risco_nivel === 'ALTO' ? '#dc3545' : '#ffc107'};">
                                        ${estudante.risco_nivel}
                                    </span>
                                </p>
                                <p><strong>Disciplinas com frequência < 75%:</strong> ${estudante.total_disciplinas_freq_baixa}</p>
                                <div class="disciplinas-problema">
                        `;
                        estudante.disciplinas_freq_baixa.forEach(d => {
                            const freqClasseDisc = (d.freq_semestral < 60) ? 'freq-muito-baixa' : 'freq-baixa';
                            html += `
                                <div class="disciplina-problema ${freqClasseDisc}">
                                    <strong>${d.disciplina}:</strong> Sem ${d.freq_semestral}% (1ºB ${d.freq_1bim || '-'}%, 2ºB ${d.freq_2bim || '-'}%)
                                </div>
                            `;
                        });
                        html += '</div></div>';
                    } else if (tipo === 'combinado') {
                        const riscoReprov = estudante.total_disciplinas_nota_baixa > 0;
                        const riscoEvasao = estudante.total_disciplinas_freq_baixa > 0 || estudante.frequencia_media_aluno < 75;
                        const classes = [
                            riscoReprov ? 'risco-reprovacao' : '',
                            riscoEvasao ? 'risco-evasao' : ''
                        ].join(' ');
                        html += `
                            <div class="estudante-item ${classes}">
                                <div class="estudante-nome"><i class="fas fa-user"></i> ${estudante.nome}</div>
                                <p><strong>Freq. Média:</strong> ${estudante.frequencia_media_aluno || '-'}%</p>
                                <p><strong>Disciplinas Nota <5:</strong> ${estudante.total_disciplinas_nota_baixa}</p>
                                <p><strong>Disciplinas Freq <75%:</strong> ${estudante.total_disciplinas_freq_baixa}</p>
                                <div class="disciplinas-problema">
                                    ${estudante.disciplinas_nota_baixa.map(d=>`<div class='disciplina-problema'>📘 ${d.disciplina}: média ${d.media}</div>`).join('')}
                                    ${estudante.disciplinas_freq_baixa.map(d=>`<div class='disciplina-problema ${d.freq_semestral<60?'freq-muito-baixa':'freq-baixa'}'>🕒 ${d.disciplina}: ${d.freq_semestral}%</div>`).join('')}
                                </div>
                            </div>`;
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
