import { useEffect, useImperativeHandle, forwardRef, useState } from 'react'

const DirectorioEmpleados = forwardRef(function DirectorioEmpleados({ onEditar, onBaja }, ref) {
  const [empleados, setEmpleados] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [textoBusqueda, setTextoBusqueda] = useState('')
  const [departamentoFiltro, setDepartamentoFiltro] = useState('')

  const cargarEmpleados = () => {
    const parametros = new URLSearchParams()
    if (textoBusqueda) parametros.set('buscar', textoBusqueda)
    if (departamentoFiltro) parametros.set('departamento', departamentoFiltro)
    const query = parametros.toString()

    fetch(`/api/empleados${query ? `?${query}` : ''}`)
      .then((respuesta) => respuesta.json())
      .then(setEmpleados)
      .catch(() => setEmpleados([]))
  }

  useEffect(cargarEmpleados, [textoBusqueda, departamentoFiltro])

  useEffect(() => {
    fetch('/api/departamentos')
      .then((respuesta) => respuesta.json())
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  useImperativeHandle(ref, () => ({ recargar: cargarEmpleados }))

  return (
    <div>
      <input
        type="text"
        data-testid="buscar-empleados"
        placeholder="Buscar por nombre o correo"
        value={textoBusqueda}
        onChange={(evento) => setTextoBusqueda(evento.target.value)}
      />
      <select
        data-testid="filtro-departamento"
        value={departamentoFiltro}
        onChange={(evento) => setDepartamentoFiltro(evento.target.value)}
      >
        <option value="">Todos los departamentos</option>
        {departamentos.map((departamento) => (
          <option key={departamento} value={departamento}>
            {departamento}
          </option>
        ))}
      </select>

      {empleados.length === 0 ? (
        <p data-testid="sin-resultados">No se encontraron resultados</p>
      ) : (
        <table data-testid="tabla-empleados">
          <thead>
            <tr>
              <th>Número</th>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Puesto</th>
              <th>Departamento</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empleados.map((empleado) => (
              <tr key={empleado.id} data-testid={`fila-empleado-${empleado.id}`}>
                <td data-testid={`numero-empleado-${empleado.id}`}>{empleado.numero_empleado}</td>
                <td>{empleado.nombre}</td>
                <td>{empleado.correo}</td>
                <td>{empleado.puesto}</td>
                <td>{empleado.departamento}</td>
                <td data-testid={`estado-empleado-${empleado.id}`}>
                  {empleado.estado === 'baja' ? 'Baja' : 'Activo'}
                </td>
                <td>
                  <button
                    type="button"
                    data-testid={`editar-empleado-${empleado.id}`}
                    onClick={() => onEditar?.(empleado)}
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    data-testid={`baja-empleado-${empleado.id}`}
                    onClick={() => onBaja?.(empleado)}
                  >
                    Dar de baja
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
})

export default DirectorioEmpleados
