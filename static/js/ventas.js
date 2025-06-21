// Scripts específicos para la página de ventas
console.log('✅ ventas.js cargado');

let clienteSeleccionado = null;
let itemsVenta = [];

function limpiarSugerencias(id) {
  const cont = document.getElementById(id);
  cont.innerHTML = '';
  cont.classList.add('hidden');
}

async function buscarCliente() {
  const q = document.getElementById('buscar_cliente').value.trim();
  const sugerencias = document.getElementById('sugerencias_cliente');
  if (!q) {
    limpiarSugerencias('sugerencias_cliente');
    return;
  }
  try {
    const resp = await fetch(`/ventas/buscar_cliente?q=${encodeURIComponent(q)}`);
    if (!resp.ok) return;
    const clientes = await resp.json();
    sugerencias.innerHTML = '';
    clientes.forEach(c => {
      const div = document.createElement('div');
      div.textContent = `${c.nombre} ${c.apellido} (${c.telefono})`;
      div.classList.add('cursor-pointer', 'py-1');
      div.addEventListener('click', () => seleccionarCliente(c));
      sugerencias.appendChild(div);
    });
    sugerencias.classList.toggle('hidden', clientes.length === 0);
  } catch (err) {
    console.error(err);
  }
}

function seleccionarCliente(c) {
  clienteSeleccionado = c;
  document.getElementById('cliente_nombre').value = c.nombre;
  document.getElementById('cliente_apellido').value = c.apellido;
  document.getElementById('cliente_telefono').value = c.telefono;
  limpiarSugerencias('sugerencias_cliente');
}

async function buscarProducto() {
  const q = document.getElementById('buscar_producto').value.trim();
  const sugerencias = document.getElementById('sugerencias_producto');
  if (!q) {
    limpiarSugerencias('sugerencias_producto');
    return;
  }
  try {
    const resp = await fetch(`/ventas/buscar_producto?q=${encodeURIComponent(q)}`);
    if (!resp.ok) return;
    const productos = await resp.json();
    sugerencias.innerHTML = '';
    productos.forEach(p => {
      const div = document.createElement('div');
      div.textContent = `${p.nombre} ${p.talle || ''} ${p.color || ''} - $${p.precio_venta}`;
      div.classList.add('cursor-pointer', 'py-1');
      div.addEventListener('click', () => agregarProducto(p));
      sugerencias.appendChild(div);
    });
    sugerencias.classList.toggle('hidden', productos.length === 0);
  } catch (err) {
    console.error(err);
  }
}

function agregarProducto(p) {
  limpiarSugerencias('sugerencias_producto');
  document.getElementById('buscar_producto').value = '';
  const cantidad = parseInt(prompt(`Cantidad para ${p.nombre}`, '1'), 10) || 1;
  const itemExistente = itemsVenta.find(i => i.producto_id === p.id);
  if (itemExistente) {
    itemExistente.cantidad += cantidad;
  } else {
    itemsVenta.push({
      producto_id: p.id,
      nombre: p.nombre,
      precio_unitario: p.precio_venta,
      cantidad: cantidad,
      descuento_aplicado: 0
    });
  }
  renderItems();
}

function renderItems() {
  const lista = document.getElementById('lista-items');
  lista.innerHTML = '';
  itemsVenta.forEach((item, idx) => {
    const div = document.createElement('div');
    div.classList.add('flex', 'justify-between', 'items-center', 'gap-2');
    div.innerHTML = `
      <span>${item.nombre} x${item.cantidad}</span>
      <span>$${(item.precio_unitario * item.cantidad).toFixed(2)}</span>
      <button type="button" data-rm="${idx}">❌</button>`;
    lista.appendChild(div);
  });
  lista.querySelectorAll('button[data-rm]').forEach(btn => {
    btn.addEventListener('click', () => {
      const idx = parseInt(btn.getAttribute('data-rm'), 10);
      itemsVenta.splice(idx, 1);
      renderItems();
    });
  });
  recalcular();
}

function recalcular() {
  const totalOriginal = itemsVenta.reduce((t, it) => t + it.precio_unitario * it.cantidad, 0);
  document.getElementById('total_original').value = totalOriginal.toFixed(2);
  const descuento = parseFloat(document.getElementById('descuento_total').value) || 0;
  const sugerido = totalOriginal - descuento;
  document.getElementById('total_cobrado').placeholder = sugerido.toFixed(2);
}

async function registrarVenta(ev) {
  ev.preventDefault();
  if (!itemsVenta.length) {
    alert('Agregue al menos un producto');
    return;
  }
  const data = {
    cliente_id: clienteSeleccionado ? clienteSeleccionado.id : null,
    cliente_nombre: document.getElementById('cliente_nombre').value,
    cliente_apellido: document.getElementById('cliente_apellido').value,
    cliente_telefono: document.getElementById('cliente_telefono').value,
    items: itemsVenta.map(it => ({
      producto_id: it.producto_id,
      cantidad: it.cantidad,
      precio_unitario: it.precio_unitario,
      precio_cobrado: it.precio_unitario * it.cantidad - (it.descuento_aplicado || 0),
      descuento_aplicado: it.descuento_aplicado || 0
    })),
    total_original: parseFloat(document.getElementById('total_original').value) || 0,
    descuento_total: parseFloat(document.getElementById('descuento_total').value) || 0,
    total_cobrado: parseFloat(document.getElementById('total_cobrado').value) || 0,
    metodo_pago: document.getElementById('metodo_pago').value
  };
  try {
    const resp = await fetch('/ventas/registrar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (resp.ok) {
      alert('Venta registrada correctamente');
      window.location.reload();
    } else {
      const err = await resp.json();
      alert(err.error || 'Error al registrar');
    }
  } catch (e) {
    console.error(e);
    alert('Error de red');
  }
}
