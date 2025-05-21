import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, RadioButtons
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class LatticeVisualizer:
    def __init__(self, problem='CVP', dimension='2D'):
        # Initialize plot
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(12, 12))
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.25)
        self.fig.patch.set_facecolor('#1e1e1e')
        
        # Initialize axes
        self.dimension = dimension
        if dimension == '3D':
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.ax.set_facecolor('#2a2a2a')
            self.ax.xaxis.set_pane_color((0.16, 0.16, 0.16, 1.0))
            self.ax.yaxis.set_pane_color((0.16, 0.16, 0.16, 1.0))
            self.ax.zaxis.set_pane_color((0.16, 0.16, 0.16, 1.0))
            self.ax.set_zlabel('Z-axis', fontsize=12, color='white')
        else:
            self.ax = self.fig.add_subplot(111)
            self.ax.set_facecolor('#2a2a2a')
            self.ax.axhline(0, color='gray', lw=0.5, alpha=0.5)
            self.ax.axvline(0, color='gray', lw=0.5, alpha=0.5)
        
        self.ax.grid(True, linestyle='--', alpha=0.5, color='lightgray')
        self.ax.set_xlabel('X-axis', fontsize=12, color='white')
        self.ax.set_ylabel('Y-axis', fontsize=12, color='white')
        self.ax.tick_params(colors='white')
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)
        if dimension == '3D':
            self.ax.set_zlim(-10, 10)
        
        # Initialize basis vectors and target
        self.b1 = np.array([4.0, 1.0, 0.0] if dimension == '3D' else [4.0, 1.0])
        self.b2 = np.array([1.0, 3.0, 0.0] if dimension == '3D' else [1.0, 3.0])
        self.b3 = np.array([0.0, 0.0, 2.0]) if dimension == '3D' else None
        self.target = np.array([2.5, 1.5, 1.0] if dimension == '3D' else [2.5, 1.5])
        self.a_range = 3 if dimension == '3D' else 5
        self.b_range = self.a_range
        self.problem = problem
        
        # Plot elements
        self.scatter = None
        self.target_scatter = None
        self.b1_quiver = None
        self.b2_quiver = None
        self.b3_quiver = None
        self.patch = None
        self.closest_quiver = None
        self.residual_quiver = None
        self.short_quivers = []
        self.closest_annotation = None
        self.target_annotation = None
        self.short_annotations = []
        
        # Setup sliders
        self.setup_sliders()
        self.update_plot()
        
        # Setup mode selector
        self.ax_mode = plt.axes([0.75, 0.85, 0.15, 0.1], facecolor='#4a4a4a')
        self.mode_selector = RadioButtons(self.ax_mode, ['CVP 2D', 'CVP 3D', 'SVP 2D', 'SVP 3D'], active=0)
        self.mode_selector.on_clicked(self.change_mode)
    
    def generate_lattice(self):
        lattice_points = []
        if self.dimension == '3D':
            for a in range(-self.a_range, self.a_range + 1):
                for b in range(-self.b_range, self.b_range + 1):
                    for c in range(-self.a_range, self.a_range + 1):
                        point = a * self.b1 + b * self.b2 + c * self.b3
                        lattice_points.append(point)
        else:
            for a in range(-self.a_range, self.a_range + 1):
                for b in range(-self.b_range, self.b_range + 1):
                    point = a * self.b1 + b * self.b2
                    lattice_points.append(point)
        return np.array(lattice_points)
    
    def find_closest_vector(self, lattice_points):
        distances = np.linalg.norm(lattice_points - self.target, axis=1)
        min_index = np.argmin(distances)
        return lattice_points[min_index], distances[min_index]
    
    def find_short_vectors(self, lattice_points, num_vectors=5):
        non_zero_vectors = lattice_points[np.any(lattice_points != 0, axis=1)]
        if len(non_zero_vectors) == 0:
            return np.array([]), np.array([])
        lengths = np.linalg.norm(non_zero_vectors, axis=1)
        sorted_indices = np.argsort(lengths)[:min(num_vectors, len(lengths))]
        return non_zero_vectors[sorted_indices], lengths[sorted_indices]
    
    def setup_sliders(self):
        axcolor = '#4a4a4a'
        slider_label_color = 'white'
        self.sliders = []
        
        # Lattice range slider
        ax_range = plt.axes([0.15, 0.22, 0.4, 0.03], facecolor=axcolor)
        max_range = 5 if self.dimension == '3D' else 10
        s_range = Slider(ax_range, 'Lattice Range', 1, max_range, valinit=self.a_range, valstep=1, color='SlateGray')
        s_range.label.set_color(slider_label_color)
        self.sliders.append(s_range)
        
        # Basis vector sliders
        slider_positions = [(0.15, 0.18), (0.15, 0.14), (0.15, 0.10), (0.15, 0.06), (0.15, 0.02)]
        if self.dimension == '3D':
            slider_positions.extend([(0.55, 0.22), (0.55, 0.18), (0.55, 0.14), (0.55, 0.10)])
        
        # b1 sliders
        ax_b1x = plt.axes([slider_positions[0][0], slider_positions[0][1], 0.4, 0.03], facecolor=axcolor)
        s_b1x = Slider(ax_b1x, 'b1_x', -5, 5, valinit=self.b1[0], valstep=0.1, color='chartreuse')
        s_b1x.label.set_color(slider_label_color)
        self.sliders.append(s_b1x)
        
        ax_b1y = plt.axes([slider_positions[1][0], slider_positions[1][1], 0.4, 0.03], facecolor=axcolor)
        s_b1y = Slider(ax_b1y, 'b1_y', -5, 5, valinit=self.b1[1], valstep=0.1, color='chartreuse')
        s_b1y.label.set_color(slider_label_color)
        self.sliders.append(s_b1y)
        
        if self.dimension == '3D':
            ax_b1z = plt.axes([slider_positions[2][0], slider_positions[2][1], 0.4, 0.03], facecolor=axcolor)
            s_b1z = Slider(ax_b1z, 'b1_z', -5, 5, valinit=self.b1[2], valstep=0.1, color='chartreuse')
            s_b1z.label.set_color(slider_label_color)
            self.sliders.append(s_b1z)
        
        # b2 sliders
        ax_b2x = plt.axes([slider_positions[2 if self.dimension == '2D' else 3][0], slider_positions[2 if self.dimension == '2D' else 3][1], 0.4, 0.03], facecolor=axcolor)
        s_b2x = Slider(ax_b2x, 'b2_x', -5, 5, valinit=self.b2[0], valstep=0.1, color='cyan')
        s_b2x.label.set_color(slider_label_color)
        self.sliders.append(s_b2x)
        
        ax_b2y = plt.axes([slider_positions[3 if self.dimension == '2D' else 4][0], slider_positions[3 if self.dimension == '2D' else 4][1], 0.4, 0.03], facecolor=axcolor)
        s_b2y = Slider(ax_b2y, 'b2_y', -5, 5, valinit=self.b2[1], valstep=0.1, color='cyan')
        s_b2y.label.set_color(slider_label_color)
        self.sliders.append(s_b2y)
        
        if self.dimension == '3D':
            ax_b2z = plt.axes([slider_positions[5][0], slider_positions[5][1], 0.4, 0.03], facecolor=axcolor)
            s_b2z = Slider(ax_b2z, 'b2_z', -5, 5, valinit=self.b2[2], valstep=0.1, color='cyan')
            s_b2z.label.set_color(slider_label_color)
            self.sliders.append(s_b2z)
        
            # b3 sliders
            ax_b3x = plt.axes([slider_positions[6][0], slider_positions[6][1], 0.4, 0.03], facecolor=axcolor)
            s_b3x = Slider(ax_b3x, 'b3_x', -5, 5, valinit=self.b3[0], valstep=0.1, color='magenta')
            s_b3x.label.set_color(slider_label_color)
            self.sliders.append(s_b3x)
            
            ax_b3y = plt.axes([slider_positions[7][0], slider_positions[7][1], 0.4, 0.03], facecolor=axcolor)
            s_b3y = Slider(ax_b3y, 'b3_y', -5, 5, valinit=self.b3[1], valstep=0.1, color='magenta')
            s_b3y.label.set_color(slider_label_color)
            self.sliders.append(s_b3y)
            
            ax_b3z = plt.axes([slider_positions[8][0], slider_positions[8][1], 0.4, 0.03], facecolor=axcolor)
            s_b3z = Slider(ax_b3z, 'b3_z', -5, 5, valinit=self.b3[2], valstep=0.1, color='magenta')
            s_b3z.label.set_color(slider_label_color)
            self.sliders.append(s_b3z)
        
        # Target sliders (for CVP only)
        if self.problem == 'CVP':
            ax_tx = plt.axes([0.55, 0.06, 0.4, 0.03], facecolor=axcolor)
            s_tx = Slider(ax_tx, 't_x', -10, 10, valinit=self.target[0], valstep=0.1, color='red')
            s_tx.label.set_color(slider_label_color)
            self.sliders.append(s_tx)
            
            ax_ty = plt.axes([0.55, 0.02, 0.4, 0.03], facecolor=axcolor)
            s_ty = Slider(ax_ty, 't_y', -10, 10, valinit=self.target[1], valstep=0.1, color='red')
            s_ty.label.set_color(slider_label_color)
            self.sliders.append(s_ty)
            
            if self.dimension == '3D':
                ax_tz = plt.axes([0.55, -0.02, 0.4, 0.03], facecolor=axcolor)
                s_tz = Slider(ax_tz, 't_z', -10, 10, valinit=self.target[2], valstep=0.1, color='red')
                s_tz.label.set_color(slider_label_color)
                self.sliders.append(s_tz)
        
        for slider in self.sliders:
            slider.on_changed(self.update)
    
    def update_plot(self):
        # Clear previous elements
        if self.scatter:
            self.scatter.remove()
        if self.target_scatter:
            self.target_scatter.remove()
        if self.b1_quiver:
            self.b1_quiver.remove()
        if self.b2_quiver:
            self.b2_quiver.remove()
        if self.b3_quiver:
            self.b3_quiver.remove()
        if self.patch:
            self.patch.remove()
        if self.closest_quiver:
            self.closest_quiver.remove()
        if self.residual_quiver:
            self.residual_quiver.remove()
        for quiver in self.short_quivers:
            quiver.remove()
        self.short_quivers.clear()
        if self.closest_annotation:
            self.closest_annotation.remove()
        if self.target_annotation:
            self.target_annotation.remove()
        for annot in self.short_annotations:
            annot.remove()
        self.short_annotations.clear()
        
        # Generate lattice points
        lattice_points = self.generate_lattice()
        
        # Plot lattice points
        if self.dimension == '3D':
            self.scatter = self.ax.scatter3D(lattice_points[:, 0], lattice_points[:, 1], lattice_points[:, 2],
                                            c='SlateGray', s=40, alpha=0.7, label='Lattice Points')
        else:
            self.scatter = self.ax.scatter(lattice_points[:, 0], lattice_points[:, 1],
                                          c='SlateGray', s=60, alpha=0.7, label='Lattice Points')
        
        # Plot basis vectors
        if self.dimension == '3D':
            self.b1_quiver = self.ax.quiver3D(0, 0, 0, self.b1[0], self.b1[1], self.b1[2],
                                             length=1, color='chartreuse', label=f'b1 = ({self.b1[0]:.1f}, {self.b1[1]:.1f}, {self.b1[2]:.1f})')
            self.b2_quiver = self.ax.quiver3D(0, 0, 0, self.b2[0], self.b2[1], self.b2[2],
                                             length=1, color='cyan', label=f'b2 = ({self.b2[0]:.1f}, {self.b2[1]:.1f}, {self.b2[2]:.1f})')
            self.b3_quiver = self.ax.quiver3D(0, 0, 0, self.b3[0], self.b3[1], self.b3[2],
                                             length=1, color='magenta', label=f'b3 = ({self.b3[0]:.1f}, {self.b3[1]:.1f}, {self.b3[2]:.1f})')
        else:
            self.b1_quiver = self.ax.quiver(0, 0, self.b1[0], self.b1[1],
                                           angles='xy', scale_units='xy', scale=1,
                                           color='chartreuse', label=f'b1 = ({self.b1[0]:.1f}, {self.b1[1]:.1f})')
            self.b2_quiver = self.ax.quiver(0, 0, self.b2[0], self.b2[1],
                                           angles='xy', scale_units='xy', scale=1,
                                           color='cyan', label=f'b2 = ({self.b2[0]:.1f}, {self.b2[1]:.1f})')
        
        # Plot fundamental domain
        if self.dimension == '3D':
            verts = [list(zip([0, self.b1[0], self.b1[0]+self.b2[0], self.b2[0], 0],
                              [0, self.b1[1], self.b1[1]+self.b2[1], self.b2[1], 0],
                              [0, self.b1[2], self.b1[2]+self.b2[2], self.b2[2], 0])),
                     list(zip([0, 0, self.b3[0], self.b3[0], 0],
                              [0, self.b2[1], self.b2[1]+self.b3[1], self.b3[1], 0],
                              [0, self.b2[2], self.b2[2]+self.b3[2], self.b3[2], 0]))]
            self.patch = Poly3DCollection(verts, alpha=0.3, color='purple', label='Fundamental Domain')
            self.ax.add_collection3d(self.patch)
        else:
            parallelogram = np.array([[0, 0], self.b1, self.b1 + self.b2, self.b2])
            self.patch = Polygon(parallelogram, closed=True, fill=True, alpha=0.3,
                                 color='purple', label='Fundamental Domain')
            self.ax.add_patch(self.patch)
        
        # Plot problem-specific elements
        if self.problem == 'CVP':
            # Plot target point
            if self.dimension == '3D':
                self.target_scatter = self.ax.scatter3D(self.target[0], self.target[1], self.target[2],
                                                       c='red', s=100, marker='*', label='Target Point')
            else:
                self.target_scatter = self.ax.scatter(self.target[0], self.target[1],
                                                     c='red', s=100, marker='*', label='Target Point')
            
            # Find and plot closest vector
            closest_point, closest_distance = self.find_closest_vector(lattice_points)
            if self.dimension == '3D':
                self.closest_quiver = self.ax.quiver3D(0, 0, 0, closest_point[0], closest_point[1], closest_point[2],
                                                      length=1, color='yellow', label=f'Closest Point (dist={closest_distance:.2f})')
                self.residual_quiver = self.ax.quiver3D(closest_point[0], closest_point[1], closest_point[2],
                                                       self.target[0] - closest_point[0], self.target[1] - closest_point[1], self.target[2] - closest_point[2],
                                                       length=1, color='orange', label='Residual Vector')
                self.closest_annotation = self.ax.text(closest_point[0], closest_point[1], closest_point[2],
                                                     f'Closest: ({closest_point[0]:.0f}, {closest_point[1]:.0f}, {closest_point[2]:.0f})\ndist={closest_distance:.2f}',
                                                     color='yellow', fontsize=10, zorder=15, ha='right', va='bottom')
                self.target_annotation = self.ax.text(self.target[0], self.target[1], self.target[2],
                                                    f'Target: ({self.target[0]:.1f}, {self.target[1]:.1f}, {self.target[2]:.1f})',
                                                    color='red', fontsize=10, zorder=15, ha='right', va='bottom')
            else:
                self.closest_quiver = self.ax.quiver(0, 0, closest_point[0], closest_point[1],
                                                    angles='xy', scale_units='xy', scale=1,
                                                    color='yellow', label=f'Closest Point (dist={closest_distance:.2f})')
                self.residual_quiver = self.ax.quiver(closest_point[0], closest_point[1],
                                                     self.target[0] - closest_point[0], self.target[1] - closest_point[1],
                                                     angles='xy', scale_units='xy', scale=1,
                                                     color='orange', label='Residual Vector')
                self.closest_annotation = self.ax.annotate(f'Closest: ({closest_point[0]:.0f}, {closest_point[1]:.0f})\ndist={closest_distance:.2f}',
                                                          xy=closest_point, xytext=(-30, 10),
                                                          textcoords='offset points', color='yellow',
                                                          fontsize=10, zorder=15)
                self.target_annotation = self.ax.annotate(f'Target: ({self.target[0]:.1f}, {self.target[1]:.1f})',
                                                         xy=self.target, xytext=(-30, 10),
                                                         textcoords='offset points', color='red',
                                                         fontsize=10, zorder=15)
        else:  # SVP
            short_vectors, short_lengths = self.find_short_vectors(lattice_points)
            colors = ['#ff69b4', '#ffa500', '#ffff99', '#90ee90', '#ff4040']
            labels = ['Short Vector 1', 'Short Vector 2', 'Short Vector 3', 'Short Vector 4', 'Short Vector 5']
            for i, (vec, length, color, label) in enumerate(zip(short_vectors, short_lengths, colors, labels)):
                if self.dimension == '3D':
                    quiver = self.ax.quiver3D(0, 0, 0, vec[0], vec[1], vec[2],
                                             length=1, color=color, label=f'{label} (len={length:.2f})',
                                             zorder=10 if i == 4 else 5)
                    annot = self.ax.text(vec[0], vec[1], vec[2],
                                        f'({vec[0]:.0f}, {vec[1]:.0f}, {vec[2]:.0f})\nlen={length:.2f}',
                                        color=color, fontsize=10, zorder=15, ha='right', va='bottom')
                else:
                    quiver = self.ax.quiver(0, 0, vec[0], vec[1],
                                           angles='xy', scale_units='xy', scale=1,
                                           color=color, label=f'{label} (len={length:.2f})',
                                           zorder=10 if i == 4 else 5)
                    annot = self.ax.annotate(f'({vec[0]:.0f}, {vec[1]:.0f})\nlen={length:.2f}',
                                            xy=vec, xytext=(-30, 10),
                                            textcoords='offset points', color=color,
                                            fontsize=10, zorder=15)
                self.short_quivers.append(quiver)
                self.short_annotations.append(annot)
        
        # Update title and legend
        title = f"Interactive {'Closest' if self.problem == 'CVP' else 'Shortest'} Vector Problem ({self.dimension})"
        self.ax.set_title(title, fontsize=14, pad=15, color='white')
        self.ax.legend(loc='upper left', fontsize=10, labelcolor='white')
        if self.dimension == '2D':
            self.ax.set_aspect('equal')
        self.fig.canvas.draw_idle()
    
    def update(self, val):
        self.a_range = self.b_range = int(self.sliders[0].val)
        self.b1[0] = self.sliders[1].val
        self.b1[1] = self.sliders[2].val
        slider_idx = 3
        if self.dimension == '3D':
            self.b1[2] = self.sliders[slider_idx].val
            slider_idx += 1
        self.b2[0] = self.sliders[slider_idx].val
        slider_idx += 1
        self.b2[1] = self.sliders[slider_idx].val
        slider_idx += 1
        if self.dimension == '3D':
            self.b2[2] = self.sliders[slider_idx].val
            slider_idx += 1
            self.b3[0] = self.sliders[slider_idx].val
            slider_idx += 1
            self.b3[1] = self.sliders[slider_idx].val
            slider_idx += 1
            self.b3[2] = self.sliders[slider_idx].val
            slider_idx += 1
        if self.problem == 'CVP':
            self.target[0] = self.sliders[slider_idx].val
            slider_idx += 1
            self.target[1] = self.sliders[slider_idx].val
            if self.dimension == '3D':
                slider_idx += 1
                self.target[2] = self.sliders[slider_idx].val
        self.update_plot()
    
    def change_mode(self, label):
        self.problem, self.dimension = label.split()
        plt.close(self.fig)
        visualizer = LatticeVisualizer(self.problem, self.dimension)
        plt.show()

if __name__ == '__main__':
    visualizer = LatticeVisualizer()
    plt.savefig('lattice_visualization.png')
    plt.show()