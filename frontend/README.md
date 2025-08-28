# Sistema Clínico - Frontend Angular

Sistema de Gestión Integral de Imágenes Diagnósticas con una interfaz moderna e intuitiva.

## 🚀 Características

- **UI Moderna y Responsiva**: Diseño limpio y profesional con Angular Material
- **Navegación Intuitiva**: Sidebar organizado y header funcional
- **Gestión de Citas**: Sistema completo para agendar y administrar citas médicas
- **Gestión de Pacientes**: Administración de información de pacientes
- **Gestión de Estudios**: Control de estudios diagnósticos
- **Sistema de Notificaciones**: Alertas y recordatorios en tiempo real
- **Tema Adaptativo**: Soporte para tema claro y oscuro
- **Completamente Funcional**: Todos los botones y funcionalidades operativas

## 🛠️ Tecnologías Utilizadas

- **Angular 20**: Framework principal
- **Angular Material**: Componentes de UI
- **TypeScript**: Lenguaje de programación
- **SCSS**: Estilos avanzados
- **RxJS**: Programación reactiva
- **CSS Variables**: Sistema de diseño consistente

## 📋 Prerrequisitos

- **Node.js**: Versión 18 o superior
- **npm**: Gestor de paquetes de Node.js
- **Angular CLI**: Herramienta de línea de comandos de Angular

## 🔧 Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd proyecto/frontend
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Verificar instalación**
   ```bash
   ng version
   ```

## 🚀 Ejecución

### Desarrollo
```bash
npm start
# o
ng serve
```

La aplicación estará disponible en: `http://localhost:4200`

### Construcción para Producción
```bash
npm run build
# o
ng build --configuration production
```

### Ejecutar Tests
```bash
npm test
# o
ng test
```

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── citas/           # Gestión de citas médicas
│   │   │   ├── pacientes/       # Gestión de pacientes
│   │   │   ├── estudios/        # Gestión de estudios
│   │   │   ├── informes/        # Informes y reportes
│   │   │   ├── notificaciones/  # Sistema de notificaciones
│   │   │   ├── header/          # Cabecera principal
│   │   │   ├── sidebar/         # Navegación lateral
│   │   │   └── footer/          # Pie de página
│   │   ├── services/
│   │   │   └── api.ts          # Servicio de API
│   │   ├── app.config.ts       # Configuración de la aplicación
│   │   ├── app.routes.ts       # Rutas de la aplicación
│   │   └── app.ts              # Componente principal
│   ├── environments/            # Variables de entorno
│   ├── styles.scss             # Estilos globales
│   └── main.ts                 # Punto de entrada
├── angular.json                # Configuración de Angular
├── package.json               # Dependencias del proyecto
└── README.md                  # Este archivo
```

## 🎨 Sistema de Diseño

### Colores Principales
- **Primary**: Azul (#1a73e8) - Acciones principales
- **Success**: Verde (#10b981) - Éxito y confirmación
- **Warning**: Amarillo (#f59e0b) - Advertencias
- **Error**: Rojo (#ef4444) - Errores y alertas
- **Info**: Azul claro (#3b82f6) - Información

### Tipografía
- **Familia**: Inter (Google Fonts)
- **Tamaños**: Sistema de escala consistente
- **Pesos**: 300, 400, 500, 600, 700, 800

### Espaciado
- **Sistema de 8px**: Base para márgenes y padding
- **Escala**: xs(4px), sm(8px), md(16px), lg(24px), xl(32px)

## 🔌 Funcionalidades Principales

### Gestión de Citas
- ✅ Agendar nuevas citas
- ✅ Editar citas existentes
- ✅ Eliminar citas
- ✅ Confirmar citas
- ✅ Filtros avanzados
- ✅ Búsqueda en tiempo real
- ✅ Estados visuales claros

### Sistema de Navegación
- ✅ Header funcional con menús
- ✅ Sidebar organizado por secciones
- ✅ Navegación entre módulos
- ✅ Indicadores de estado activo
- ✅ Menús desplegables

### Interfaz de Usuario
- ✅ Diseño responsive
- ✅ Animaciones suaves
- ✅ Estados de carga
- ✅ Mensajes de confirmación
- ✅ Tema adaptativo

## 📱 Responsive Design

- **Desktop**: 1024px y superior
- **Tablet**: 768px - 1023px
- **Mobile**: 767px e inferior

## 🎯 Componentes Clave

### Header
- Logo y título del sistema
- Navegación principal
- Sistema de notificaciones
- Perfil de usuario con menú

### Sidebar
- Navegación por módulos
- Agrupación lógica de funciones
- Indicadores de estado
- Información del usuario

### Citas
- Formulario de agendamiento
- Lista de citas con filtros
- Estados visuales claros
- Acciones contextuales

## 🚀 Despliegue

### Netlify
```bash
npm run build
# Subir la carpeta dist/ a Netlify
```

### Vercel
```bash
npm run build
# Subir la carpeta dist/ a Vercel
```

### Servidor Tradicional
```bash
npm run build
# Copiar la carpeta dist/ al servidor web
```

## 🧪 Testing

```bash
# Ejecutar tests unitarios
npm test

# Ejecutar tests con coverage
ng test --code-coverage

# Ejecutar tests e2e
ng e2e
```

## 🔧 Configuración

### Variables de Entorno
- **development**: `http://localhost:3000`
- **production**: URL del backend en producción

### Angular Material
- Tema: Indigo-Pink
- Personalización completa de componentes
- Overrides para consistencia visual

## 📊 Rendimiento

- **Lazy Loading**: Carga bajo demanda de módulos
- **Optimización de imágenes**: WebP y formatos modernos
- **Minificación**: CSS y JavaScript optimizados
- **Tree Shaking**: Eliminación de código no utilizado

## 🔒 Seguridad

- **XSS Protection**: Headers de seguridad
- **Content Security Policy**: Políticas de contenido
- **HTTPS**: Conexiones seguras
- **Validación de formularios**: Entrada de datos segura

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar la documentación técnica

## 🎉 Estado del Proyecto

✅ **Completado**: UI moderna y funcional
✅ **Completado**: Todos los botones operativos
✅ **Completado**: Sistema de navegación
✅ **Completado**: Gestión de citas
✅ **Completado**: Diseño responsive
✅ **Completado**: Tema adaptativo
✅ **Completado**: Listo para despliegue

---

**Desarrollado con ❤️ para el Sistema Clínico**
