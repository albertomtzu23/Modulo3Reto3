import { useRef, useState } from 'react'
import FormularioEmpleado from './FormularioEmpleado'
import DirectorioEmpleados from './DirectorioEmpleados'
import EditarEmpleado from './EditarEmpleado'
import BajaEmpleado from './BajaEmpleado'
import './App.css'

function App() {
  const directorioRef = useRef(null)
  const [accion, setAccion] = useState(null)

  const recargarYCerrar = () => {
    directorioRef.current?.recargar()
    setAccion(null)
  }

  return (
    <main>
      {accion === null && (
        <FormularioEmpleado onEmpleadoCreado={() => directorioRef.current?.recargar()} />
      )}
      {accion?.tipo === 'editar' && (
        <EditarEmpleado
          empleado={accion.empleado}
          onGuardado={recargarYCerrar}
          onCancelar={() => setAccion(null)}
        />
      )}
      {accion?.tipo === 'baja' && (
        <BajaEmpleado
          empleado={accion.empleado}
          onConfirmada={recargarYCerrar}
          onCancelar={() => setAccion(null)}
        />
      )}
      <DirectorioEmpleados
        ref={directorioRef}
        onEditar={(empleado) => setAccion({ tipo: 'editar', empleado })}
        onBaja={(empleado) => setAccion({ tipo: 'baja', empleado })}
      />
    </main>
  )
}

export default App
