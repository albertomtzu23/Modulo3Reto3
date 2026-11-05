import { useEffect, useState } from 'react'

const ESTADO_INICIAL = {
  nombre: '',
  correo: '',
  puesto: '',
  departamento: '',
  fecha_ingreso: '',
}

function FormularioEmpleado({ onEmpleadoCreado }) {
  const [departamentos, setDepartamentos] = useState([])
  const [datos, setDatos] = useState(ESTADO_INICIAL)
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')
  const [campoInvalido, setCampoInvalido] = useState('')

  useEffect(() => {
    fetch('/api/departamentos')
      .then((respuesta) => respuesta.json())
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  const actualizarCampo = (campo) => (evento) => {
    setDatos({ ...datos, [campo]: evento.target.value })
  }

  const enviarFormulario = async (evento) => {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')
    setCampoInvalido('')

    try {
      const respuesta = await fetch('/api/empleados', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos),
      })
      const cuerpo = await respuesta.json()

      if (!respuesta.ok) {
        const detalle = cuerpo.detail || 'No se pudo registrar al empleado'
        setMensajeError(detalle)
        const campo = ['nombre', 'correo', 'puesto', 'departamento', 'fecha_ingreso'].find(
          (nombreCampo) => detalle.includes(`'${nombreCampo}'`),
        )
        if (campo) setCampoInvalido(campo)
        return
      }

      setMensajeExito(`Empleado ${cuerpo.numero_empleado} registrado con éxito`)
      setDatos(ESTADO_INICIAL)
      onEmpleadoCreado?.()
    } catch {
      setMensajeError('No se pudo contactar al servidor')
    }
  }

  return (
    <form onSubmit={enviarFormulario}>
      <h1>Registrar empleado</h1>

      <label htmlFor="empleado-nombre">Nombre</label>
      <input
        id="empleado-nombre"
        data-testid="empleado-nombre"
        type="text"
        value={datos.nombre}
        onChange={actualizarCampo('nombre')}
        aria-invalid={campoInvalido === 'nombre'}
        required
      />

      <label htmlFor="empleado-correo">Correo</label>
      <input
        id="empleado-correo"
        data-testid="empleado-correo"
        type="email"
        value={datos.correo}
        onChange={actualizarCampo('correo')}
        required
      />

      <label htmlFor="empleado-puesto">Puesto</label>
      <input
        id="empleado-puesto"
        data-testid="empleado-puesto"
        type="text"
        value={datos.puesto}
        onChange={actualizarCampo('puesto')}
        required
      />

      <label htmlFor="empleado-departamento">Departamento</label>
      <select
        id="empleado-departamento"
        data-testid="empleado-departamento"
        value={datos.departamento}
        onChange={actualizarCampo('departamento')}
        required
      >
        <option value="">Selecciona un departamento</option>
        {departamentos.map((departamento) => (
          <option key={departamento} value={departamento}>
            {departamento}
          </option>
        ))}
      </select>

      <label htmlFor="empleado-fecha-ingreso">Fecha de ingreso</label>
      <input
        id="empleado-fecha-ingreso"
        data-testid="empleado-fecha-ingreso"
        type="date"
        value={datos.fecha_ingreso}
        onChange={actualizarCampo('fecha_ingreso')}
        required
      />

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default FormularioEmpleado
