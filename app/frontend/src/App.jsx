import { useRef, useState } from 'react'
import FormularioEmpleado from './FormularioEmpleado'
import DirectorioEmpleados from './DirectorioEmpleados'
import EditarEmpleado from './EditarEmpleado'
import BajaEmpleado from './BajaEmpleado'
import VacacionesEmpleado from './VacacionesEmpleado'
import './App.css'

function App() {
  const directorioRef = useRef(null)
  const [accion, setAccion] = useState(null)
  const [mensajeExito, setMensajeExito] = useState('')

  const abrirAccion = (accionNueva) => {
    setMensajeExito('')
    setAccion(accionNueva)
  }

  const manejarExito = (texto) => {
    directorioRef.current?.recargar()
    setAccion(null)
    setMensajeExito(texto)
  }

  return (
    <main>
      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {accion === null && (
        <FormularioEmpleado
          onEmpleadoCreado={() => {
            setMensajeExito('')
            directorioRef.current?.recargar()
          }}
        />
      )}
      {accion?.tipo === 'editar' && (
        <EditarEmpleado
          empleado={accion.empleado}
          onGuardado={manejarExito}
          onCancelar={() => setAccion(null)}
        />
      )}
      {accion?.tipo === 'baja' && (
        <BajaEmpleado
          empleado={accion.empleado}
          onConfirmada={manejarExito}
          onCancelar={() => setAccion(null)}
        />
      )}
      {accion?.tipo === 'vacaciones' && (
        <VacacionesEmpleado
          empleado={accion.empleado}
          onCerrar={() => setAccion(null)}
        />
      )}
      <DirectorioEmpleados
        ref={directorioRef}
        onEditar={(empleado) => abrirAccion({ tipo: 'editar', empleado })}
        onBaja={(empleado) => abrirAccion({ tipo: 'baja', empleado })}
        onVacaciones={(empleado) => abrirAccion({ tipo: 'vacaciones', empleado })}
      />
    </main>
  )
}

export default App
