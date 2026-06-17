// src/gs/web/main.js

const socket = io();

const elEstado = document.getElementById('enlace-status');
const elModo = document.getElementById('val-modo');
const elSeq = document.getElementById('val-seq');
const elBat = document.getElementById('val-bat');
const elTmp = document.getElementById('val-tmp');
const elPwr = document.getElementById('val-pwr');
const btnPayload = document.getElementById('btn-payload');
const logComandos = document.getElementById('log-comandos');

let temporizadorLOS;
let orbitTrail = []; // Guardará el histórico de coordenadas para dibujar la traza
let satX = 0;
let satY = 0;

setInterval(() => {
    const now = new Date();
    document.getElementById('reloj-utc').innerText = now.toISOString().substr(11, 8) + ' UTC';
}, 1000);

Chart.defaults.color = '#a0aab5';
Chart.defaults.font.family = "'Share Tech Mono', monospace";

const ctxBat = document.getElementById('chart-bat').getContext('2d');
const chartBat = new Chart(ctxBat, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Batería (%)', data: [], borderColor: '#39ff14', tension: 0.4 }] },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 0, max: 100 } }, animation: false }
});

const ctxTmp = document.getElementById('chart-tmp').getContext('2d');
const chartTmp = new Chart(ctxTmp, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Temperatura (ºC)', data: [], borderColor: '#ff9900', tension: 0.4 }] },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: -40, max: 80 } }, animation: false }
});

socket.on('telemetria_satelite', (paquete) => {
    elEstado.innerText = "AOS (ENLACE ESTABLE)";
    elEstado.className = "status-aos";
    btnPayload.disabled = false;

    clearTimeout(temporizadorLOS);
    temporizadorLOS = setTimeout(() => {
        elEstado.innerText = "LOS (SIN SEÑAL)";
        elEstado.className = "status-los";
        btnPayload.disabled = true;
    }, 3000);

    elSeq.innerText = paquete.seq;
    elModo.innerText = paquete.mod;
    elModo.style.color = (paquete.mod === 'SEGURO') ? '#ff2a2a' : '#00f0ff';
    elBat.innerText = paquete.bat.toFixed(1) + ' %';
    elTmp.innerText = paquete.tmp.toFixed(1) + ' ºC';
    elPwr.innerText = paquete.pwr.toFixed(1) + ' W';

    if (chartBat.data.labels.length > 50) {
        chartBat.data.labels.shift();
        chartBat.data.datasets[0].data.shift();
        chartTmp.data.labels.shift();
        chartTmp.data.datasets[0].data.shift();
    }
    
    chartBat.data.labels.push(paquete.seq);
    chartBat.data.datasets[0].data.push(paquete.bat);
    chartBat.update();

    chartTmp.data.labels.push(paquete.seq);
    chartTmp.data.datasets[0].data.push(paquete.tmp);
    chartTmp.update();

    // Transformación Matemática: Lat/Lon a coordenadas (X,Y) del Canvas
    const canvas = document.getElementById('canvas-orbita');
    // Longitud: -180 a +180 mapeado de 0 a Ancho
    satX = ((paquete.lon + 180) / 360) * canvas.width;
    // Latitud: +90 a -90 mapeado de 0 a Alto
    satY = ((-paquete.lat + 90) / 180) * canvas.height;
    
    orbitTrail.push({x: satX, y: satY});
    if(orbitTrail.length > 200) orbitTrail.shift(); // Evitar que el array crezca al infinito
});

btnPayload.addEventListener('click', () => {
    const comando = { id: Date.now(), cmd: "PAYLOAD_ON", val: 10 };
    socket.emit('enviar_telecomando', comando);
    logComandos.innerHTML += `<br>[TX] PAYLOAD_ON (+10W)`;
    logComandos.scrollTop = logComandos.scrollHeight;
});

const canvas = document.getElementById('canvas-orbita');
const ctx = canvas.getContext('2d');

function redimensionarCanvas() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
}
window.addEventListener('resize', redimensionarCanvas);
redimensionarCanvas();

function dibujarRadar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Dibujar la traza orbital (Histórico)
    if (orbitTrail.length > 0) {
        ctx.beginPath();
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 2;
        for (let i = 0; i < orbitTrail.length; i++) {
            let pt = orbitTrail[i];
            if (i === 0) {
                ctx.moveTo(pt.x, pt.y);
            } else {
                let ptAnt = orbitTrail[i-1];
                // Evitar dibujar una línea recta cuando el satélite cruza de un lado a otro del mapa (Antimeridiano)
                if (Math.abs(pt.x - ptAnt.x) > canvas.width / 2) {
                    ctx.moveTo(pt.x, pt.y);
                } else {
                    ctx.lineTo(pt.x, pt.y);
                }
            }
        }
        ctx.stroke();
    }

    // Dibujar el punto del Satélite en vivo
    if (satX !== 0 && satY !== 0) {
        ctx.beginPath();
        ctx.arc(satX, satY, 5, 0, Math.PI * 2);
        ctx.fillStyle = (elEstado.className === 'status-aos') ? '#39ff14' : '#ff9900';
        ctx.fill();
        ctx.shadowBlur = 10;
        ctx.shadowColor = ctx.fillStyle;
    }

    // Coordenadas de Madrid proyectadas
    const madridX = ((-3.7038 + 180) / 360) * canvas.width;
    const madridY = ((-40.4168 + 90) / 180) * canvas.height;
    
    ctx.shadowBlur = 0; // Apagar brillo para dibujar antena
    ctx.beginPath();
    ctx.arc(madridX, madridY, 40, 0, Math.PI * 2); // Rango de antena
    ctx.fillStyle = 'rgba(255, 42, 42, 0.1)';
    ctx.fill();
    ctx.strokeStyle = '#ff2a2a';
    ctx.setLineDash([2, 4]);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#ff2a2a';
    ctx.font = '10px Share Tech Mono';
    ctx.fillText("MADRID", madridX + 10, madridY - 10);
    
    requestAnimationFrame(dibujarRadar);
}

dibujarRadar();