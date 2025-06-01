from manim import *
import numpy as np
import itertools

class NCubeVisualizer(ThreeDScene):
    def construct(self):
        # Configuración de la cámara 3D
        self.set_camera_orientation(phi=60 * DEGREES, theta=30 * DEGREES)
        
        # Crear un hipercubo 4D (2x2x2x2)
        hypercube_data = np.zeros((2, 2, 2, 2))
        for indices in itertools.product([0, 1], repeat=4):
            hypercube_data[indices] = np.sum(indices) / 4
        
        # Visualizar la secuencia completa
        self.visualize_dimension_reduction(hypercube_data)
    
    def visualize_dimension_reduction(self, data_4d):
        """Visualiza la secuencia completa de reducción dimensional"""
        # Título general
        title = Text("Reducción Dimensional con np.mean", font_size=36)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # Crear la secuencia de datos reducidos
        data_3d = np.mean(data_4d, axis=3)  # 4D -> 3D
        data_2d = np.mean(data_3d, axis=2)  # 3D -> 2D
        data_1d = np.mean(data_2d, axis=1)  # 2D -> 1D
        data_0d = np.mean(data_1d, axis=0)  # 1D -> 0D
        
        dimension_data = [data_4d, data_3d, data_2d, data_1d, data_0d]
        dimension_names = ["Teseracto (4D)", "Cubo (3D)", "Cuadrado (2D)", "Línea (1D)", "Punto (0D)"]
        axis_reduced = [3, 2, 1, 0]
        
        # Iniciar con 4D
        subtitle = Text(dimension_names[0], font_size=28)
        subtitle.next_to(title, DOWN)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle))
        
        # Crear la estructura 4D inicial
        current_structure = self.create_ncube(data_4d)
        self.play(Create(current_structure))
        
        # Rotar para explorar
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(3)
        self.stop_ambient_camera_rotation()
        
        # Recorrer cada dimensión
        for i in range(4):
            # Actualizar subtítulo
            new_subtitle = Text(dimension_names[i+1], font_size=28)
            new_subtitle.next_to(title, DOWN)
            self.add_fixed_in_frame_mobjects(new_subtitle)
            
            # Mostrar fórmula de reducción
            formula = MathTex(r"\text{np.mean(data, axis=", f"{axis_reduced[i]}", r")}")
            formula.scale(0.8)
            formula.to_corner(UL).shift(DOWN * 0.5 + RIGHT * 1.0)
            self.add_fixed_in_frame_mobjects(formula)
            
            self.play(
                FadeOut(subtitle),
                FadeIn(new_subtitle),
                FadeIn(formula)
            )
            subtitle = new_subtitle
            
            # Crear estructura de la siguiente dimensión
            next_structure = self.create_ncube(dimension_data[i+1], include_labels=(i+1 < 4))
            
            # Transformar entre dimensiones con morphing completo
            self.play(
                ReplacementTransform(current_structure, next_structure),
                run_time=2.5
            )
            current_structure = next_structure
            
            # Ajustar la cámara según la dimensión
            if i == 0:  # 4D -> 3D: mantener vista 3D
                pass
            elif i == 1:  # 3D -> 2D: vista superior para cuadrado
                self.move_camera(phi=0 * DEGREES, theta=0 * DEGREES, run_time=1)
            elif i == 2:  # 2D -> 1D: vista lateral para línea
                self.move_camera(phi=0 * DEGREES, theta=90 * DEGREES, run_time=1)
            
            # Rotación para explorar (solo para 3D+)
            if i < 1:  # Para 4D y 3D
                self.begin_ambient_camera_rotation(rate=0.15)
                self.wait(3)
                self.stop_ambient_camera_rotation()
            else:
                self.wait(2)
            
            # Limpiar fórmula
            self.play(FadeOut(formula))
        
        # Mensaje final
        final_message = Text("Reducción completa: 4D → 0D", font_size=32)
        final_message.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(final_message)
        self.play(Write(final_message))
        self.wait(2)
    
    def create_ncube(self, data, include_labels=True):
        """Crea una representación visual de un n-cubo con sus vértices, aristas y etiquetas"""
        # Determinar dimensionalidad
        if np.isscalar(data):
            n_dims = 0
        else:
            n_dims = len(data.shape)
        
        # Grupo principal que contendrá todos los elementos
        ncube = VGroup()
        
        # Caso especial para 0D: un solo punto
        if n_dims == 0:
            value = float(data)
            vertex = Sphere(radius=0.2, resolution=(20, 20))
            vertex.set_color(self.value_to_color(value))
            
            # Etiqueta para valor
            if include_labels:
                value_label = DecimalNumber(value, num_decimal_places=2, font_size=24)
                value_label.next_to(vertex, UP, buff=0.2)
                self.add_fixed_orientation_mobjects(value_label)
                ncube.add(value_label)
            
            ncube.add(vertex)
            return ncube
        
        # Para dimensiones superiores
        vertices = VGroup()
        edges = VGroup()
        labels = VGroup()
        
        # Generar coordenadas de vértices
        vertex_coords = list(itertools.product([0, 1], repeat=n_dims))
        vertex_map = {}  # Mapeo entre coordenadas y objetos
        
        # Crear vértices
        for coords in vertex_coords:
            # Calcular posición en el espacio 3D
            pos = self.get_vertex_position(coords, n_dims)
            
            # Obtener valor
            try:
                if n_dims == 1:
                    value = float(data[coords[0]])
                else:
                    value = float(data[coords])
            except (IndexError, TypeError):
                value = 0
            
            # Crear vértice
            vertex = Sphere(radius=0.1, resolution=(15, 15))
            vertex.set_color(self.value_to_color(value))
            vertex.move_to(pos)
            vertices.add(vertex)
            
            # Guardar referencia para crear aristas
            vertex_map[coords] = vertex
            
            # Etiquetas (valor y coordenadas)
            if include_labels:
                value_label = DecimalNumber(value, num_decimal_places=2, font_size=20)
                value_label.move_to(pos + UP * 0.25)
                self.add_fixed_orientation_mobjects(value_label)
                labels.add(value_label)
                
                if n_dims > 1:
                    # Etiqueta con letras (A, B, C, etc.) en lugar de coordenadas
                    coord_text = "".join([self.dim_to_letter(i) for i, v in enumerate(coords) if v == 1])
                    if not coord_text:
                        coord_text = "O"  # Origen
                    
                    coord_label = Text(coord_text, font_size=16)
                    coord_label.move_to(pos + DOWN * 0.25)
                    self.add_fixed_orientation_mobjects(coord_label)
                    labels.add(coord_label)
        
        # Crear aristas
        if n_dims >= 1:
            for i, coords1 in enumerate(vertex_coords):
                for coords2 in vertex_coords[i+1:]:
                    # Aristas conectan vértices que difieren en una sola coordenada
                    if sum(a != b for a, b in zip(coords1, coords2)) == 1:
                        # ¿Qué dimensión cambió?
                        dim_changed = next((i for i, (a, b) in enumerate(zip(coords1, coords2)) if a != b), None)
                        
                        # Color según dimensión
                        dim_colors = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE]
                        edge_color = dim_colors[dim_changed % len(dim_colors)]
                        
                        # Arista 3D
                        start = vertex_map[coords1].get_center()
                        end = vertex_map[coords2].get_center()
                        edge = Line3D(start=start, end=end, color=edge_color)
                        edges.add(edge)
        
        # Leyendas y referencias
        if n_dims > 1 and include_labels:
            # Leyenda de dimensiones
            dim_labels = VGroup()
            for d in range(n_dims):
                letter = self.dim_to_letter(d)
                dim_colors = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE]
                color = dim_colors[d % len(dim_colors)]
                dim_label = Text(f"Dim {letter}", font_size=20, color=color)
                dim_label.to_corner(UL).shift(DOWN * (d * 0.4 + 0.5) + RIGHT * 0.5)
                self.add_fixed_in_frame_mobjects(dim_label)
                dim_labels.add(dim_label)
            
            # Leyenda de colores
            color_legend = self.create_color_legend()
            self.add_fixed_in_frame_mobjects(color_legend)
        
        # Añadir todos los componentes al grupo principal
        ncube.add(edges, vertices, labels)
        return ncube
    
    def get_vertex_position(self, coords, n_dims):
        """Calcula la posición 3D de un vértice según sus coordenadas n-dimensionales"""
        if n_dims == 1:
            # 1D: línea en eje X
            return np.array([coords[0] * 2 - 1, 0, 0])
        elif n_dims == 2:
            # 2D: cuadrado en plano XY
            return np.array([coords[0] * 2 - 1, coords[1] * 2 - 1, 0])
        elif n_dims == 3:
            # 3D: cubo en espacio XYZ
            return np.array([coords[0] * 2 - 1, coords[1] * 2 - 1, coords[2] * 2 - 1])
        else:
            # 4D+: cubo anidado
            base = np.array([coords[0] * 2 - 1, coords[1] * 2 - 1, coords[2] * 2 - 1])
            
            # Factor de escala/desplazamiento para dimensiones superiores
            for i in range(3, n_dims):
                if coords[i] == 1:
                    factor = 0.35
                    base = base * (1 + coords[i] * factor)
            
            return base
    
    def dim_to_letter(self, dim):
        """Convierte índice de dimensión a letra (0->A, 1->B, etc.)"""
        return chr(65 + dim)
    
    def create_color_legend(self):
        """Crea leyenda para la escala de colores"""
        segments = 10
        gradient_group = VGroup()
        
        for i in range(segments):
            t = i / (segments - 1)
            color = self.value_to_color(t)
            segment = Rectangle(
                height=0.3,
                width=3/segments,
                fill_color=color,
                fill_opacity=1,
                stroke_width=0
            ).shift(RIGHT * (3/segments) * (i - segments/2 + 0.5))
            gradient_group.add(segment)
        
        # Borde
        border = Rectangle(height=0.3, width=3, stroke_color=WHITE, stroke_width=1, fill_opacity=0)
        gradient_group.add(border)
        
        # Etiquetas
        min_label = Text("0.0", font_size=16).next_to(gradient_group, LEFT)
        max_label = Text("1.0", font_size=16).next_to(gradient_group, RIGHT)
        title = Text("Valor", font_size=20).next_to(gradient_group, UP)
        
        legend = VGroup(gradient_group, min_label, max_label, title)
        legend.to_corner(DR)
        
        return legend
    
    def value_to_color(self, value):
        """Mapea valor a color en escala azul-rojo"""
        value = min(max(float(value), 0), 1)
        return interpolate_color(BLUE, RED, value)


class DimensionalReduction(NCubeVisualizer):
    """Clase optimizada para la visualización de reducción dimensional"""
    def construct(self):
        # Configuración inicial
        self.set_camera_orientation(phi=60 * DEGREES, theta=30 * DEGREES)
        
        # Datos 4D de prueba
        hypercube_data = np.zeros((2, 2, 2, 2))
        for indices in itertools.product([0, 1], repeat=4):
            hypercube_data[indices] = np.sum(indices) / 4
        
        # Ejecutar visualización
        self.visualize_dimension_reduction(hypercube_data)


# Para ejecutar:
# manim -pql ncube_visualizer.py DimensionalReduction