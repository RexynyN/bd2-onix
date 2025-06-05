// Library Management System JavaScript

// In-memory database simulation
let database = {
    usuarios: [
        { id_usuario: 1, nome: 'João Silva', email: 'joao@email.com', endereco: 'Rua A, 123', telefone: '(11) 99999-9999' },
        { id_usuario: 2, nome: 'Maria Santos', email: 'maria@email.com', endereco: 'Rua B, 456', telefone: '(11) 88888-8888' },
        { id_usuario: 3, nome: 'Pedro Costa', email: 'pedro@email.com', endereco: 'Rua C, 789', telefone: '(11) 77777-7777' }
    ],
    bibliotecas: [
        { id_biblioteca: 1, nome: 'Biblioteca Central', endereco: 'Av. Principal, 100' },
        { id_biblioteca: 2, nome: 'Biblioteca Norte', endereco: 'Rua Norte, 200' }
    ],
    midias: [
        { id_midia: 1, tipo_midia: 'livro', titulo: 'Dom Casmurro', condicao: 'excelente', id_biblioteca: 1, ISBN: '978-85-359-0277-5', numero_paginas: 256, editora: 'Ática', data_publicacao: '2010-05-15' },
        { id_midia: 2, tipo_midia: 'revista', titulo: 'National Geographic', condicao: 'boa', id_biblioteca: 1, ISSN: '0027-9358', periodicidade: 'Mensal', editora: 'National Geographic Society', data_publicacao: '2023-01-01' },
        { id_midia: 3, tipo_midia: 'dvd', titulo: 'O Senhor dos Anéis', condicao: 'excelente', id_biblioteca: 2, ISAN: '0000-0000-9E59-0000-0-0000-0000-2', duracao: 178, distribuidora: 'Warner Bros', data_lancamento: '2001-12-19' },
        { id_midia: 4, tipo_midia: 'artigo', titulo: 'Inteligência Artificial no Século XXI', condicao: 'excelente', id_biblioteca: 1, DOI: '10.1000/182', publicadora: 'IEEE', data_publicacao: '2023-03-15' }
    ],
    emprestimos: [
        { id_emprestimo: 1, data_emprestimo: '2024-05-01', data_devolucao_prevista: '2024-05-15', data_devolucao: null, id_midia: 1, id_usuario: 1 },
        { id_emprestimo: 2, data_emprestimo: '2024-05-10', data_devolucao_prevista: '2024-05-24', data_devolucao: '2024-05-20', id_midia: 2, id_usuario: 2 },
        { id_emprestimo: 3, data_emprestimo: '2024-04-20', data_devolucao_prevista: '2024-05-04', data_devolucao: null, id_midia: 3, id_usuario: 3 }
    ],
    penalizacoes: [],
    autores: [
        { id_autor: 1, nome: 'Machado de Assis', data_nascimento: '1839-06-21', data_falecimento: '1908-09-29' },
        { id_autor: 2, nome: 'J.R.R. Tolkien', data_nascimento: '1892-01-03', data_falecimento: '1973-09-02' }
    ],
    autorias: [
        { id_autorias: 1, id_autor: 1, id_midia: 1 },
        { id_autorias: 2, id_autor: 2, id_midia: 3 }
    ]
};

// Current view state
let currentView = 'dashboard';
let currentTab = 'usuarios';
let currentFilter = 'todos';

// Chart instance
let mediaTypeChart = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    showView('dashboard');
    updateDashboardStats();
    renderAllTables();
    populateDropdowns();
    initializeChart();
    setActiveNavLink();
}

// View Management
function showView(viewName) {
    // Hide all views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    
    // Show selected view
    document.getElementById(viewName + '-view').classList.add('active');
    currentView = viewName;
    
    // Update navigation
    setActiveNavLink();
    
    // Update content based on view
    if (viewName === 'dashboard') {
        updateDashboardStats();
        updateChart();
    } else if (viewName === 'biblioteca') {
        renderAllTables();
    } else if (viewName === 'emprestimos') {
        renderEmprestimosTable();
        populateEmprestimoDropdowns();
    }
}

function setActiveNavLink() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const links = document.querySelectorAll('.nav-link');
    if (currentView === 'dashboard') links[0].classList.add('active');
    else if (currentView === 'biblioteca') links[1].classList.add('active');
    else if (currentView === 'emprestimos') links[2].classList.add('active');
}

// Tab Management
function showManagementTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.management-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    currentTab = tabName;
    
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Render appropriate table
    renderTable(tabName);
}

// Dashboard Functions
function updateDashboardStats() {
    document.getElementById('total-usuarios').textContent = database.usuarios.length;
    document.getElementById('total-midias').textContent = database.midias.length;
    document.getElementById('emprestimos-ativos').textContent = 
        database.emprestimos.filter(emp => !emp.data_devolucao).length;
    document.getElementById('total-bibliotecas').textContent = database.bibliotecas.length;
}

function initializeChart() {
    const ctx = document.getElementById('mediaTypeChart').getContext('2d');
    
    const mediaTypeCounts = {
        'livro': 0,
        'revista': 0,
        'dvd': 0,
        'artigo': 0
    };
    
    database.emprestimos.forEach(emp => {
        const midia = database.midias.find(m => m.id_midia === emp.id_midia);
        if (midia) {
            mediaTypeCounts[midia.tipo_midia]++;
        }
    });
    
    mediaTypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Livros', 'Revistas', 'DVDs', 'Artigos'],
            datasets: [{
                data: [
                    mediaTypeCounts.livro,
                    mediaTypeCounts.revista,
                    mediaTypeCounts.dvd,
                    mediaTypeCounts.artigo
                ],
                backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

function updateChart() {
    if (mediaTypeChart) {
        const mediaTypeCounts = {
            'livro': 0,
            'revista': 0,
            'dvd': 0,
            'artigo': 0
        };
        
        database.emprestimos.forEach(emp => {
            const midia = database.midias.find(m => m.id_midia === emp.id_midia);
            if (midia) {
                mediaTypeCounts[midia.tipo_midia]++;
            }
        });
        
        mediaTypeChart.data.datasets[0].data = [
            mediaTypeCounts.livro,
            mediaTypeCounts.revista,
            mediaTypeCounts.dvd,
            mediaTypeCounts.artigo
        ];
        
        mediaTypeChart.update();
    }
}

// Table Rendering
function renderAllTables() {
    renderTable('usuarios');
    renderTable('bibliotecas');
    renderTable('midias');
    renderTable('autores');
    renderEmprestimosTable();
}

function renderTable(tableName) {
    const tableBody = document.querySelector(`#${tableName}-table tbody`);
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    const data = database[tableName];
    if (!data || data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="100%" class="empty-state">Nenhum registro encontrado</td></tr>';
        return;
    }
    
    data.forEach(item => {
        const row = createTableRow(tableName, item);
        tableBody.appendChild(row);
    });
}

function createTableRow(tableName, item) {
    const row = document.createElement('tr');
    
    switch (tableName) {
        case 'usuarios':
            row.innerHTML = `
                <td>${item.id_usuario}</td>
                <td>${item.nome}</td>
                <td>${item.email || '-'}</td>
                <td>${item.telefone || '-'}</td>
                <td>
                    <button class="btn action-btn btn--edit" onclick="editItem('usuarios', ${item.id_usuario})">Editar</button>
                    <button class="btn action-btn btn--delete" onclick="deleteItem('usuarios', ${item.id_usuario})">Excluir</button>
                </td>
            `;
            break;
            
        case 'bibliotecas':
            row.innerHTML = `
                <td>${item.id_biblioteca}</td>
                <td>${item.nome}</td>
                <td>${item.endereco || '-'}</td>
                <td>
                    <button class="btn action-btn btn--edit" onclick="editItem('bibliotecas', ${item.id_biblioteca})">Editar</button>
                    <button class="btn action-btn btn--delete" onclick="deleteItem('bibliotecas', ${item.id_biblioteca})">Excluir</button>
                </td>
            `;
            break;
            
        case 'midias':
            const biblioteca = database.bibliotecas.find(b => b.id_biblioteca === item.id_biblioteca);
            row.innerHTML = `
                <td>${item.id_midia}</td>
                <td><span class="status-badge status-badge--info">${item.tipo_midia}</span></td>
                <td>${item.titulo}</td>
                <td>${item.condicao}</td>
                <td>${biblioteca ? biblioteca.nome : '-'}</td>
                <td>
                    <button class="btn action-btn btn--edit" onclick="editItem('midias', ${item.id_midia})">Editar</button>
                    <button class="btn action-btn btn--delete" onclick="deleteItem('midias', ${item.id_midia})">Excluir</button>
                </td>
            `;
            break;
            
        case 'autores':
            row.innerHTML = `
                <td>${item.id_autor}</td>
                <td>${item.nome}</td>
                <td>${item.data_nascimento ? formatDate(item.data_nascimento) : '-'}</td>
                <td>
                    <button class="btn action-btn btn--edit" onclick="editItem('autores', ${item.id_autor})">Editar</button>
                    <button class="btn action-btn btn--delete" onclick="deleteItem('autores', ${item.id_autor})">Excluir</button>
                </td>
            `;
            break;
    }
    
    return row;
}

function renderEmprestimosTable() {
    const tableBody = document.querySelector('#emprestimos-table tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    let emprestimos = database.emprestimos;
    
    // Apply filter
    if (currentFilter === 'ativos') {
        emprestimos = emprestimos.filter(emp => !emp.data_devolucao);
    } else if (currentFilter === 'devolvidos') {
        emprestimos = emprestimos.filter(emp => emp.data_devolucao);
    } else if (currentFilter === 'atrasados') {
        emprestimos = emprestimos.filter(emp => !emp.data_devolucao && new Date(emp.data_devolucao_prevista) < new Date());
    }
    
    if (emprestimos.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="8" class="empty-state">Nenhum empréstimo encontrado</td></tr>';
        return;
    }
    
    emprestimos.forEach(emp => {
        const usuario = database.usuarios.find(u => u.id_usuario === emp.id_usuario);
        const midia = database.midias.find(m => m.id_midia === emp.id_midia);
        const status = getEmprestimoStatus(emp);
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${emp.id_emprestimo}</td>
            <td>${usuario ? usuario.nome : 'Usuário não encontrado'}</td>
            <td>${midia ? midia.titulo : 'Mídia não encontrada'}</td>
            <td>${formatDate(emp.data_emprestimo)}</td>
            <td>${formatDate(emp.data_devolucao_prevista)}</td>
            <td>${emp.data_devolucao ? formatDate(emp.data_devolucao) : '-'}</td>
            <td><span class="status-badge status-badge--${status.class}">${status.text}</span></td>
            <td>
                ${!emp.data_devolucao ? 
                    `<button class="btn action-btn btn--return" onclick="returnEmprestimo(${emp.id_emprestimo})">Devolver</button>` : 
                    '<span class="text-secondary">-</span>'
                }
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function getEmprestimoStatus(emprestimo) {
    if (emprestimo.data_devolucao) {
        return { text: 'Devolvido', class: 'devolvido' };
    } else if (new Date(emprestimo.data_devolucao_prevista) < new Date()) {
        return { text: 'Atrasado', class: 'atrasado' };
    } else {
        return { text: 'Ativo', class: 'ativo' };
    }
}

// Filter Functions
function filterEmprestimos() {
    const filterSelect = document.getElementById('emprestimo-filter');
    currentFilter = filterSelect.value;
    renderEmprestimosTable();
}

// Modal Management
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('show');
    
    // Reset form if it's an add operation
    if (modalId.includes('modal')) {
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
            clearHiddenId(modalId);
        }
    }
    
    // Update modal title for add operations
    updateModalTitle(modalId, 'add');
    
    // Special handling for specific modals
    if (modalId === 'midia-modal') {
        populateBibliotecaDropdown();
        updateMidiaFields();
    } else if (modalId === 'emprestimo-modal') {
        populateEmprestimoDropdowns();
        setDefaultEmprestimoDates();
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
}

function updateModalTitle(modalId, action) {
    const titleMap = {
        'usuario-modal': { add: 'Adicionar Usuário', edit: 'Editar Usuário' },
        'biblioteca-modal': { add: 'Adicionar Biblioteca', edit: 'Editar Biblioteca' },
        'midia-modal': { add: 'Adicionar Mídia', edit: 'Editar Mídia' },
        'autor-modal': { add: 'Adicionar Autor', edit: 'Editar Autor' },
        'emprestimo-modal': { add: 'Novo Empréstimo', edit: 'Editar Empréstimo' }
    };
    
    const titleElement = document.getElementById(modalId.replace('-modal', '-modal-title'));
    if (titleElement && titleMap[modalId]) {
        titleElement.textContent = titleMap[modalId][action];
    }
}

// CRUD Operations
function editItem(tableName, itemId) {
    const item = database[tableName].find(i => i[getIdField(tableName)] === itemId);
    if (!item) return;
    
    const modalId = getModalId(tableName);
    showModal(modalId);
    updateModalTitle(modalId, 'edit');
    
    // Populate form fields
    populateForm(tableName, item);
}

function deleteItem(tableName, itemId) {
    if (!confirm('Tem certeza que deseja excluir este item?')) return;
    
    const index = database[tableName].findIndex(i => i[getIdField(tableName)] === itemId);
    if (index > -1) {
        database[tableName].splice(index, 1);
        renderTable(tableName);
        updateDashboardStats();
        showAlert('Item excluído com sucesso!', 'success');
    }
}

function getIdField(tableName) {
    const idFields = {
        'usuarios': 'id_usuario',
        'bibliotecas': 'id_biblioteca',
        'midias': 'id_midia',
        'autores': 'id_autor',
        'emprestimos': 'id_emprestimo'
    };
    return idFields[tableName];
}

function getModalId(tableName) {
    const modalIds = {
        'usuarios': 'usuario-modal',
        'bibliotecas': 'biblioteca-modal',
        'midias': 'midia-modal',
        'autores': 'autor-modal',
        'emprestimos': 'emprestimo-modal'
    };
    return modalIds[tableName];
}

// Form Functions
function populateForm(tableName, item) {
    switch (tableName) {
        case 'usuarios':
            document.getElementById('usuario-id').value = item.id_usuario;
            document.getElementById('usuario-nome').value = item.nome;
            document.getElementById('usuario-email').value = item.email || '';
            document.getElementById('usuario-endereco').value = item.endereco || '';
            document.getElementById('usuario-telefone').value = item.telefone || '';
            break;
            
        case 'bibliotecas':
            document.getElementById('biblioteca-id').value = item.id_biblioteca;
            document.getElementById('biblioteca-nome').value = item.nome;
            document.getElementById('biblioteca-endereco').value = item.endereco || '';
            break;
            
        case 'midias':
            document.getElementById('midia-id').value = item.id_midia;
            document.getElementById('midia-tipo').value = item.tipo_midia;
            document.getElementById('midia-titulo').value = item.titulo;
            document.getElementById('midia-condicao').value = item.condicao;
            document.getElementById('midia-biblioteca').value = item.id_biblioteca || '';
            updateMidiaFields();
            populateMidiaSpecificFields(item);
            break;
            
        case 'autores':
            document.getElementById('autor-id').value = item.id_autor;
            document.getElementById('autor-nome').value = item.nome;
            document.getElementById('autor-nascimento').value = item.data_nascimento || '';
            document.getElementById('autor-falecimento').value = item.data_falecimento || '';
            break;
    }
}

function populateMidiaSpecificFields(item) {
    // Clear existing dynamic fields first
    const dynamicFields = document.getElementById('dynamic-fields');
    const inputs = dynamicFields.querySelectorAll('input');
    inputs.forEach(input => {
        if (item[input.id.replace('midia-', '')]) {
            input.value = item[input.id.replace('midia-', '')];
        }
    });
}

function clearHiddenId(modalId) {
    const idField = modalId.replace('-modal', '-id');
    const element = document.getElementById(idField);
    if (element) element.value = '';
}

// Save Functions
function saveUsuario(event) {
    event.preventDefault();
    
    const formData = {
        nome: document.getElementById('usuario-nome').value,
        email: document.getElementById('usuario-email').value,
        endereco: document.getElementById('usuario-endereco').value,
        telefone: document.getElementById('usuario-telefone').value
    };
    
    const id = document.getElementById('usuario-id').value;
    
    if (id) {
        // Edit existing
        const index = database.usuarios.findIndex(u => u.id_usuario === parseInt(id));
        if (index > -1) {
            database.usuarios[index] = { ...database.usuarios[index], ...formData };
            showAlert('Usuário atualizado com sucesso!', 'success');
        }
    } else {
        // Add new
        const newId = Math.max(...database.usuarios.map(u => u.id_usuario), 0) + 1;
        database.usuarios.push({ id_usuario: newId, ...formData });
        showAlert('Usuário adicionado com sucesso!', 'success');
    }
    
    closeModal('usuario-modal');
    renderTable('usuarios');
    updateDashboardStats();
    populateDropdowns();
}

function saveBiblioteca(event) {
    event.preventDefault();
    
    const formData = {
        nome: document.getElementById('biblioteca-nome').value,
        endereco: document.getElementById('biblioteca-endereco').value
    };
    
    const id = document.getElementById('biblioteca-id').value;
    
    if (id) {
        // Edit existing
        const index = database.bibliotecas.findIndex(b => b.id_biblioteca === parseInt(id));
        if (index > -1) {
            database.bibliotecas[index] = { ...database.bibliotecas[index], ...formData };
            showAlert('Biblioteca atualizada com sucesso!', 'success');
        }
    } else {
        // Add new
        const newId = Math.max(...database.bibliotecas.map(b => b.id_biblioteca), 0) + 1;
        database.bibliotecas.push({ id_biblioteca: newId, ...formData });
        showAlert('Biblioteca adicionada com sucesso!', 'success');
    }
    
    closeModal('biblioteca-modal');
    renderTable('bibliotecas');
    updateDashboardStats();
    populateDropdowns();
}

function saveMidia(event) {
    event.preventDefault();
    
    const formData = {
        tipo_midia: document.getElementById('midia-tipo').value,
        titulo: document.getElementById('midia-titulo').value,
        condicao: document.getElementById('midia-condicao').value,
        id_biblioteca: parseInt(document.getElementById('midia-biblioteca').value) || null
    };
    
    // Get dynamic fields based on media type
    const dynamicInputs = document.querySelectorAll('#dynamic-fields input, #dynamic-fields select');
    dynamicInputs.forEach(input => {
        const fieldName = input.id.replace('midia-', '');
        if (input.value) {
            if (input.type === 'number') {
                formData[fieldName] = parseInt(input.value);
            } else {
                formData[fieldName] = input.value;
            }
        }
    });
    
    const id = document.getElementById('midia-id').value;
    
    if (id) {
        // Edit existing
        const index = database.midias.findIndex(m => m.id_midia === parseInt(id));
        if (index > -1) {
            database.midias[index] = { ...database.midias[index], ...formData };
            showAlert('Mídia atualizada com sucesso!', 'success');
        }
    } else {
        // Add new
        const newId = Math.max(...database.midias.map(m => m.id_midia), 0) + 1;
        database.midias.push({ id_midia: newId, ...formData });
        showAlert('Mídia adicionada com sucesso!', 'success');
    }
    
    closeModal('midia-modal');
    renderTable('midias');
    updateDashboardStats();
    updateChart();
    populateDropdowns();
}

function saveAutor(event) {
    event.preventDefault();
    
    const formData = {
        nome: document.getElementById('autor-nome').value,
        data_nascimento: document.getElementById('autor-nascimento').value || null,
        data_falecimento: document.getElementById('autor-falecimento').value || null
    };
    
    const id = document.getElementById('autor-id').value;
    
    if (id) {
        // Edit existing
        const index = database.autores.findIndex(a => a.id_autor === parseInt(id));
        if (index > -1) {
            database.autores[index] = { ...database.autores[index], ...formData };
            showAlert('Autor atualizado com sucesso!', 'success');
        }
    } else {
        // Add new
        const newId = Math.max(...database.autores.map(a => a.id_autor), 0) + 1;
        database.autores.push({ id_autor: newId, ...formData });
        showAlert('Autor adicionado com sucesso!', 'success');
    }
    
    closeModal('autor-modal');
    renderTable('autores');
}

function saveEmprestimo(event) {
    event.preventDefault();
    
    const formData = {
        id_usuario: parseInt(document.getElementById('emprestimo-usuario').value),
        id_midia: parseInt(document.getElementById('emprestimo-midia').value),
        data_emprestimo: document.getElementById('emprestimo-data').value,
        data_devolucao_prevista: document.getElementById('emprestimo-data-prevista').value,
        data_devolucao: null
    };
    
    // Check if media is already borrowed
    const existingEmprestimo = database.emprestimos.find(emp => 
        emp.id_midia === formData.id_midia && !emp.data_devolucao
    );
    
    if (existingEmprestimo) {
        showAlert('Esta mídia já está emprestada!', 'error');
        return;
    }
    
    const newId = Math.max(...database.emprestimos.map(e => e.id_emprestimo), 0) + 1;
    database.emprestimos.push({ id_emprestimo: newId, ...formData });
    
    showAlert('Empréstimo realizado com sucesso!', 'success');
    closeModal('emprestimo-modal');
    renderEmprestimosTable();
    updateDashboardStats();
    updateChart();
}

function returnEmprestimo(emprestimoId) {
    if (!confirm('Confirmar devolução deste empréstimo?')) return;
    
    const emprestimo = database.emprestimos.find(emp => emp.id_emprestimo === emprestimoId);
    if (emprestimo) {
        emprestimo.data_devolucao = new Date().toISOString().split('T')[0];
        
        // Check if it's late and create penalty
        if (new Date(emprestimo.data_devolucao) > new Date(emprestimo.data_devolucao_prevista)) {
            const newPenaltyId = Math.max(...database.penalizacoes.map(p => p.id_penalizacao), 0) + 1;
            const daysLate = Math.ceil((new Date(emprestimo.data_devolucao) - new Date(emprestimo.data_devolucao_prevista)) / (1000 * 60 * 60 * 24));
            
            database.penalizacoes.push({
                id_penalizacao: newPenaltyId,
                descricao: `Devolução com atraso de ${daysLate} dia(s)`,
                final_penalizacao: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days from now
                id_usuario: emprestimo.id_usuario,
                id_emprestimo: emprestimo.id_emprestimo
            });
            
            showAlert('Empréstimo devolvido com atraso. Penalização aplicada.', 'warning');
        } else {
            showAlert('Empréstimo devolvido com sucesso!', 'success');
        }
        
        renderEmprestimosTable();
        updateDashboardStats();
        updateChart();
    }
}

// Dynamic fields for media types
function updateMidiaFields() {
    const tipoSelect = document.getElementById('midia-tipo');
    const dynamicFields = document.getElementById('dynamic-fields');
    const tipo = tipoSelect.value;
    
    dynamicFields.innerHTML = '';
    
    const fieldConfigs = {
        'livro': [
            { id: 'ISBN', label: 'ISBN', type: 'text' },
            { id: 'numero_paginas', label: 'Número de Páginas', type: 'number' },
            { id: 'editora', label: 'Editora', type: 'text' },
            { id: 'data_publicacao', label: 'Data de Publicação', type: 'date' }
        ],
        'revista': [
            { id: 'ISSN', label: 'ISSN', type: 'text' },
            { id: 'periodicidade', label: 'Periodicidade', type: 'text' },
            { id: 'editora', label: 'Editora', type: 'text' },
            { id: 'data_publicacao', label: 'Data de Publicação', type: 'date' }
        ],
        'dvd': [
            { id: 'ISAN', label: 'ISAN', type: 'text' },
            { id: 'duracao', label: 'Duração (minutos)', type: 'number' },
            { id: 'distribuidora', label: 'Distribuidora', type: 'text' },
            { id: 'data_lancamento', label: 'Data de Lançamento', type: 'date' }
        ],
        'artigo': [
            { id: 'DOI', label: 'DOI', type: 'text' },
            { id: 'publicadora', label: 'Publicadora', type: 'text' },
            { id: 'data_publicacao', label: 'Data de Publicação', type: 'date' }
        ]
    };
    
    if (fieldConfigs[tipo]) {
        fieldConfigs[tipo].forEach(field => {
            const div = document.createElement('div');
            div.className = 'form-group dynamic-field';
            div.innerHTML = `
                <label class="form-label">${field.label}</label>
                <input type="${field.type}" class="form-control" id="midia-${field.id}">
            `;
            dynamicFields.appendChild(div);
        });
    }
}

// Dropdown population
function populateDropdowns() {
    populateBibliotecaDropdown();
    populateEmprestimoDropdowns();
}

function populateBibliotecaDropdown() {
    const select = document.getElementById('midia-biblioteca');
    if (!select) return;
    
    select.innerHTML = '<option value="">Selecione uma biblioteca</option>';
    database.bibliotecas.forEach(biblioteca => {
        const option = document.createElement('option');
        option.value = biblioteca.id_biblioteca;
        option.textContent = biblioteca.nome;
        select.appendChild(option);
    });
}

function populateEmprestimoDropdowns() {
    const usuarioSelect = document.getElementById('emprestimo-usuario');
    const midiaSelect = document.getElementById('emprestimo-midia');
    
    if (usuarioSelect) {
        usuarioSelect.innerHTML = '<option value="">Selecione um usuário</option>';
        database.usuarios.forEach(usuario => {
            const option = document.createElement('option');
            option.value = usuario.id_usuario;
            option.textContent = usuario.nome;
            usuarioSelect.appendChild(option);
        });
    }
    
    if (midiaSelect) {
        midiaSelect.innerHTML = '<option value="">Selecione uma mídia</option>';
        
        // Only show available media (not currently borrowed)
        const borrowedMidiaIds = database.emprestimos
            .filter(emp => !emp.data_devolucao)
            .map(emp => emp.id_midia);
            
        const availableMidias = database.midias.filter(midia => 
            !borrowedMidiaIds.includes(midia.id_midia)
        );
        
        availableMidias.forEach(midia => {
            const option = document.createElement('option');
            option.value = midia.id_midia;
            option.textContent = `${midia.titulo} (${midia.tipo_midia})`;
            midiaSelect.appendChild(option);
        });
    }
}

function setDefaultEmprestimoDates() {
    // Set default date for emprestimo
    const dataEmprestimo = document.getElementById('emprestimo-data');
    if (dataEmprestimo) {
        dataEmprestimo.value = new Date().toISOString().split('T')[0];
    }
    
    // Set default return date (15 days from now)
    const dataPrevista = document.getElementById('emprestimo-data-prevista');
    if (dataPrevista) {
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + 15);
        dataPrevista.value = futureDate.toISOString().split('T')[0];
    }
}

// Alert system
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert--${type}`;
    alertElement.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="closeAlert(this)">&times;</button>
    `;
    
    alertContainer.appendChild(alertElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertElement.parentNode) {
            alertElement.parentNode.removeChild(alertElement);
        }
    }, 5000);
}

function closeAlert(button) {
    const alert = button.closest('.alert');
    if (alert && alert.parentNode) {
        alert.parentNode.removeChild(alert);
    }
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        const modalId = event.target.id;
        closeModal(modalId);
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        // Close any open modals
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            closeModal(openModal.id);
        }
    }
});