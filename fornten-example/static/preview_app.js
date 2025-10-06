// --- GLOBAL STATE ---
let allBills = JSON.parse(localStorage.getItem('billBatch')) || [
    { id: "file1", supplier: "Allstar", filename: "allstar_bill_1.pdf", status: "Pending",
      data: [{ "merchant_name": "Luton Road Connect", "gross_value": "758.25" }] },
    { id: "file2", supplier: "Shell", filename: "shell_invoice_2.pdf", status: "Pending",
      data: [{ "description": "V-Power Unleaded", "quantity": "50.00", "total": "85.50" }] },
    { id: "file3", supplier: "Kennedys", filename: "kennedys_invoice.pdf", status: "Approved",
      data: [{ "item": "Professional Charges", "amount": "1535.00" }] }
];
let currentFileIndex = parseInt(localStorage.getItem('selectedBillIndex')) || 0;

// --- DOM ELEMENTS ---
const modal = document.getElementById('previewModal');
const billNameH3 = document.getElementById('billName');
const dataTable = document.getElementById('dataTable');
const approveBtn = document.getElementById('approveBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

// --- INITIALIZE ---
function initialize() {
    renderTable();
    prevBtn.addEventListener('click', () => displayBillInModal(currentFileIndex - 1));
    nextBtn.addEventListener('click', () => displayBillInModal(currentFileIndex + 1));
    approveBtn.addEventListener('click', approveCurrentBill);
}

// --- CORE FUNCTIONS ---

function renderTable() {
    // ... (This function remains unchanged from the previous version)
    const tableBody = document.getElementById('billList');
    tableBody.innerHTML = ''; 
    allBills.forEach((bill, index) => {
        const row = document.createElement('tr');
        const statusHtml = `<button class="status-button ${bill.status === 'Approved' ? 'status-approved' : 'status-pending'}" onclick="openPreview(${index})">${bill.status}</button>`;
        row.innerHTML = `
            <td>${bill.supplier}</td>
            <td>${bill.upload_date || '2025-09-18'}</td>
            <td>${bill.filename}</td>
            <td>${statusHtml}</td>
            <td>${bill.amount || '£1,000.00'}</td>
        `;
        tableBody.appendChild(row);
    });
}

function openPreview(index) {
    displayBillInModal(index);
    modal.classList.add('visible');
}

function closePreview() {
    modal.classList.remove('visible');
}

function displayBillInModal(index) {
    if (index < 0 || index >= allBills.length) return;
    
    currentFileIndex = index;
    localStorage.setItem('selectedBillIndex', currentFileIndex); // Remember the current index
    const file = allBills[index];

    billNameH3.textContent = file.filename;
    populateDataTable(file.data); // Use the stored data for this bill
    
    approveBtn.disabled = file.status === 'Approved';
    approveBtn.textContent = file.status === 'Approved' ? 'Approved' : 'Approve';
    prevBtn.disabled = index === 0;
    nextBtn.disabled = index === allBills.length - 1;
}

function approveCurrentBill() {
    const file = allBills[currentFileIndex];
    if (!file || file.status === 'Approved') return;

    // Get the edited data from the table
    const editedData = getEditedData();
    
    // Update the bill's data and status in our local list
    file.data = editedData;
    file.status = 'Approved';
    
    // KEY CHANGE: Save the entire updated list back to localStorage
    localStorage.setItem('billBatch', JSON.stringify(allBills));
    
    alert(`Simulating Approval for: ${file.filename}\nYour edits have been saved for this session.`);
    
    renderTable(); // Update the main dashboard table in the background
    closePreview();
}

function getEditedData() {
    const headers = Array.from(dataTable.querySelectorAll('thead th')).map(th => th.textContent.toLowerCase().replace(/ /g, '_'));
    const rows = dataTable.querySelectorAll('tbody tr');
    const data = [];

    rows.forEach(row => {
        const rowData = {};
        const cells = row.querySelectorAll('td');
        headers.forEach((header, index) => {
            rowData[header] = cells[index].textContent;
        });
        data.push(rowData);
    });
    return data;
}

function populateDataTable(data) {
    const tableHead = dataTable.querySelector('thead');
    const tableBody = dataTable.querySelector('tbody');
    tableHead.innerHTML = '';
    tableBody.innerHTML = '';

    if (!data || data.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="100%">No data to display.</td></tr>`;
        return;
    }

    const headers = Object.keys(data[0]);
    let headerRow = '<tr>';
    headers.forEach(h => headerRow += `<th>${h.replace(/_/g, ' ').toUpperCase()}</th>`);
    tableHead.innerHTML = headerRow + '</tr>';

    data.forEach(item => {
        let row = '<tr>';
        headers.forEach(h => row += `<td contenteditable="true">${item[h]}</td>`);
        tableBody.innerHTML += row + '</tr>';
    });
}

// --- START THE APP ---
initialize();