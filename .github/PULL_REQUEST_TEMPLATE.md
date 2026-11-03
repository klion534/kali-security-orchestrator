# Pull Request

## Qué cambia

<!-- Una o dos frases. El diff ya muestra el qué; el PR explica el porqué. -->

## Por qué

<!-- El problema que resuelve, o la decisión que toma. -->

## Relación con la feature ODD

<!--
Referencia el documento ODD de la feature y las specs cubiertas:
  Feature: odd/tasks/<nombre>.md
  Specs cubiertas: S1, S4
Si el cambio es pequeño y no requiere documento, escribe "N/A — cambio inline".
-->

## Tipo de cambio

- [ ] Funcionalidad nueva
- [ ] Fix
- [ ] Refactor (sin cambio de comportamiento)
- [ ] Documentación
- [ ] Infraestructura / CI
- [ ] Dependencia

## Checklist

- [ ] La suite pasa y pego la salida real de los tests
- [ ] Los cambios de comportamiento tienen test
- [ ] Los casos de borde del negocio están cubiertos
- [ ] No hay secretos, credenciales ni datos sensibles en el diff
- [ ] No hay `console.log`, `print` de debug ni código muerto
- [ ] El diff se lee de arriba abajo sin contexto extra
- [ ] La documentación está actualizada si cambió el comportamiento
- [ ] Las migraciones son reversibles o están documentadas

## Verificación

```
Comando: <comando exacto>
Salida:  <línea de resumen real>
```

<!-- Si no ejecutaste la suite, dilo. "Debería pasar" no es evidencia. -->

## Riesgo

<!--
Qué puede romper en producción y cómo se mitiga.
Alta | Media | Baja
-->

## Revisión

<!--
- [ ] ¿Un revisor humano aprobó?
- [ ] ¿La revisión de seguridad automática pasó?
- [ ] ¿El autor del código no es su propio revisor?
-->
