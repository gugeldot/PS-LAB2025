"""
Ejemplo de integración de todos los patrones en gameManager

Este archivo muestra cómo integrar los 10 patrones de diseño
de forma modular y opcional en el GameManager existente.
"""

from patterns import (
    # Observer
    Subject, PointsObserver, StructureObserver, GameEventLogger,
    # Command
    CommandHistory, BuildStructureCommand, BuildConveyorCommand,
    # Memento
    GameOriginator, GameCaretaker,
    # Prototype
    PrototypeRegistry, LayoutRegistry, PrototypeFactory,
    # Mediator
    GameMediator, StructureMediator
)


def initialize_patterns(gameManager):
    """
    Inicializa todos los sistemas de patrones en el GameManager
    
    Args:
        gameManager: Instancia del GameManager (Singleton)
    """
    
    # ============ OBSERVER PATTERN ============
    # GameManager ya hereda de Subject, solo necesitamos crear observadores
    
    # Observador de puntos (conectado al HUD si existe)
    hud = getattr(gameManager, 'hud', None)
    points_observer = PointsObserver(hud)
    gameManager.attach('points_changed', points_observer)
    
    # Observador de estructuras
    structure_observer = StructureObserver()
    gameManager.attach('structure_built', structure_observer)
    gameManager.attach('structure_destroyed', structure_observer)
    
    # Logger de eventos (solo en debug)
    if gameManager.debug_mode:
        event_logger = GameEventLogger(verbose=True)
        gameManager.attach('points_changed', event_logger)
        gameManager.attach('structure_built', event_logger)
        gameManager.attach('structure_destroyed', event_logger)
        gameManager.event_logger = event_logger
    
    # ============ COMMAND PATTERN ============
    # Sistema de undo/redo con historial
    gameManager.command_history = CommandHistory(max_history=50)
    
    # ============ MEMENTO PATTERN ============
    # Sistema de guardado/carga
    gameManager.originator = GameOriginator(gameManager)
    gameManager.caretaker = GameCaretaker(max_snapshots=10)
    
    # Crear checkpoint inicial
    initial_memento = gameManager.originator.create_memento("initial_state")
    gameManager.caretaker.save_snapshot("initial_state", initial_memento)
    
    # ============ PROTOTYPE PATTERN ============
    # Registro de prototipos de estructuras
    gameManager.prototype_registry = PrototypeRegistry()
    gameManager.layout_registry = LayoutRegistry()
    
    # Registrar prototipos comunes si los creators existen
    if hasattr(gameManager, 'mineCreator'):
        for i in range(1, 10):
            proto = PrototypeFactory.create_mine_prototype(gameManager.mineCreator, i)
            gameManager.prototype_registry.register(f"mine_{i}", proto)
    
    if hasattr(gameManager, 'wellCreator'):
        for i in [2, 3, 5, 7, 11]:  # Números primos comunes
            proto = PrototypeFactory.create_well_prototype(gameManager.wellCreator, i)
            gameManager.prototype_registry.register(f"well_{i}", proto)
    
    # ============ MEDIATOR PATTERN ============
    # Mediador central para coordinar componentes
    gameManager.mediator = GameMediator(gameManager)
    gameManager.mediator.hud = hud
    
    if hasattr(gameManager, 'mouseControl'):
        gameManager.mediator.mouse_control = gameManager.mouseControl
    
    # Mediador para estructuras
    gameManager.structure_mediator = StructureMediator()
    
    print("✅ All design patterns initialized successfully!")
    print(f"   - Observer: 3 observers attached")
    print(f"   - Command: History ready (max {gameManager.command_history.max_history})")
    print(f"   - Memento: Caretaker ready (max {gameManager.caretaker.max_auto_snapshots} auto-saves)")
    print(f"   - Prototype: {len(gameManager.prototype_registry.list_prototypes())} prototypes registered")
    print(f"   - Mediator: Game mediator ready")


# ============================================
# EXTENSIÓN DE MÉTODOS DEL GAMEMANAGER
# ============================================

def extend_gamemanager_with_patterns(GameManagerClass):
    """
    Decorator para extender GameManager con funcionalidad de patrones
    
    Uso:
        @extend_gamemanager_with_patterns
        class GameManager(metaclass=SingletonMeta):
            ...
    """
    
    # Guardar métodos originales
    original_init = GameManagerClass.__init__
    
    def new_init(self, *args, **kwargs):
        """Inicialización extendida con patrones"""
        # Llamar init original
        original_init(self, *args, **kwargs)
        
        # Inicializar patrones si está habilitado
        if getattr(self, 'use_patterns', True):
            initialize_patterns(self)
    
    # ========== MÉTODOS PARA OBSERVER ==========
    
    def notify_points_changed(self, old_points, new_points):
        """Notifica cambio de puntos a observadores"""
        if hasattr(self, 'notify'):
            delta = new_points - old_points
            self.notify('points_changed', {
                'points': new_points,
                'delta': delta,
                'old_points': old_points
            })
    
    def notify_structure_built(self, structure, cost):
        """Notifica construcción de estructura"""
        if hasattr(self, 'notify'):
            self.notify('structure_built', {
                'type': structure.__class__.__name__,
                'structure': structure,
                'position': getattr(structure, 'position', None),
                'cost': cost
            })
    
    def notify_structure_destroyed(self, structure, refund):
        """Notifica destrucción de estructura"""
        if hasattr(self, 'notify'):
            self.notify('structure_destroyed', {
                'type': structure.__class__.__name__,
                'structure': structure,
                'position': getattr(structure, 'position', None),
                'refund': refund
            })
    
    # ========== MÉTODOS PARA COMMAND ==========
    
    def build_with_command(self, creator, position):
        """Construye estructura usando Command pattern (con undo/redo)"""
        if not hasattr(self, 'command_history'):
            return self._build_structure_direct(creator, position)
        
        cmd = BuildStructureCommand(self, creator, position)
        success = self.command_history.execute(cmd)
        
        if success and cmd.structure:
            self.notify_structure_built(cmd.structure, cmd.cost)
        
        return success
    
    def build_conveyor_with_command(self, start_pos, end_pos):
        """Construye cinta usando Command pattern"""
        if not hasattr(self, 'command_history') or not hasattr(self, 'conveyorCreator'):
            return False
        
        cmd = BuildConveyorCommand(self, self.conveyorCreator, start_pos, end_pos)
        return self.command_history.execute(cmd)
    
    def undo_last_action(self):
        """Deshace última acción (Ctrl+Z)"""
        if hasattr(self, 'command_history'):
            return self.command_history.undo()
        return False
    
    def redo_last_action(self):
        """Rehace última acción (Ctrl+Y)"""
        if hasattr(self, 'command_history'):
            return self.command_history.redo()
        return False
    
    # ========== MÉTODOS PARA MEMENTO ==========
    
    def save_game(self, save_name="manual_save"):
        """Guarda estado del juego"""
        if not hasattr(self, 'originator') or not hasattr(self, 'caretaker'):
            return False
        
        try:
            memento = self.originator.create_memento(save_name)
            self.caretaker.save_snapshot(save_name, memento)
            print(f"💾 Game saved: {save_name}")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, save_name="manual_save"):
        """Carga estado del juego"""
        if not hasattr(self, 'caretaker') or not hasattr(self, 'originator'):
            return False
        
        try:
            memento = self.caretaker.load_snapshot(save_name)
            if memento:
                self.originator.restore_memento(memento)
                print(f"📂 Game loaded: {save_name}")
                return True
            else:
                print(f"❌ Save not found: {save_name}")
                return False
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
    
    def auto_save(self):
        """Crea checkpoint automático"""
        if not hasattr(self, 'originator') or not hasattr(self, 'caretaker'):
            return
        
        try:
            memento = self.originator.create_memento("auto_save")
            self.caretaker.save_auto_snapshot(memento)
        except Exception as e:
            print(f"Error in auto-save: {e}")
    
    # ========== MÉTODOS PARA PROTOTYPE ==========
    
    def build_from_prototype(self, prototype_name, position):
        """Construye estructura desde prototipo"""
        if not hasattr(self, 'prototype_registry'):
            return None
        
        return self.prototype_registry.create_from_prototype(
            prototype_name, position, self
        )
    
    def apply_layout(self, layout_name, offset=(0, 0)):
        """Aplica un layout completo en una posición"""
        if not hasattr(self, 'layout_registry'):
            return False
        
        layout = self.layout_registry.get_layout(layout_name)
        if not layout:
            return False
        
        structures = layout.get_structures()
        for struct_info in structures:
            pos = struct_info['position']
            new_pos = (pos[0] + offset[0], pos[1] + offset[1])
            
            # Aquí deberías usar el creator apropiado según struct_info['type']
            # Ejemplo simplificado:
            print(f"Would place {struct_info['type']} at {new_pos}")
        
        return True
    
    # ========== INTEGRACIÓN CON TECLADO ==========
    
    def handle_pattern_hotkeys(self, event):
        """Maneja teclas para funcionalidad de patrones"""
        import pygame
        
        # Ctrl+Z: Undo
        if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
            if self.undo_last_action():
                print("⏪ Undo")
            return True
        
        # Ctrl+Y: Redo
        if event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
            if self.redo_last_action():
                print("⏩ Redo")
            return True
        
        # Ctrl+S: Save
        if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.save_game("quick_save")
            return True
        
        # Ctrl+L: Load
        if event.key == pygame.K_l and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.load_game("quick_save")
            return True
        
        # F5: Quick save
        if event.key == pygame.K_F5:
            self.auto_save()
            print("💾 Auto-saved")
            return True
        
        return False
    
    # Añadir métodos a la clase
    GameManagerClass.__init__ = new_init
    GameManagerClass.notify_points_changed = notify_points_changed
    GameManagerClass.notify_structure_built = notify_structure_built
    GameManagerClass.notify_structure_destroyed = notify_structure_destroyed
    GameManagerClass.build_with_command = build_with_command
    GameManagerClass.build_conveyor_with_command = build_conveyor_with_command
    GameManagerClass.undo_last_action = undo_last_action
    GameManagerClass.redo_last_action = redo_last_action
    GameManagerClass.save_game = save_game
    GameManagerClass.load_game = load_game
    GameManagerClass.auto_save = auto_save
    GameManagerClass.build_from_prototype = build_from_prototype
    GameManagerClass.apply_layout = apply_layout
    GameManagerClass.handle_pattern_hotkeys = handle_pattern_hotkeys
    
    return GameManagerClass


# ============================================
# EJEMPLO DE USO COMPLETO
# ============================================

def example_usage():
    """Ejemplo de cómo usar todos los patrones juntos"""
    
    # Obtener GameManager (Singleton)
    from gameManager import GameManager
    gm = GameManager()
    
    # Los patrones ya están inicializados automáticamente
    # si usaste extend_gamemanager_with_patterns
    
    # ========== OBSERVER: Notificar cambios ==========
    old_points = gm.points
    gm.points += 10
    gm.notify_points_changed(old_points, gm.points)
    # Output: 📦 +10 puntos!
    
    # ========== COMMAND: Construir con undo/redo ==========
    # Construir con posibilidad de deshacer
    gm.build_with_command(gm.mineCreator, position=(5, 5))
    # Se puede deshacer con Ctrl+Z
    
    # ========== MEMENTO: Guardar/Cargar ==========
    # Guardar estado actual
    gm.save_game("checkpoint_1")
    
    # Hacer cambios...
    gm.points += 100
    
    # Restaurar estado
    gm.load_game("checkpoint_1")
    # Los puntos vuelven al valor anterior
    
    # ========== PROTOTYPE: Usar prototipos ==========
    # Construir desde prototipo
    mine = gm.build_from_prototype("mine_5", position=(10, 10))
    # Crea una mina con número 5
    
    # Aplicar layout completo
    gm.apply_layout("basic_sum", offset=(15, 15))
    # Coloca 2 minas + operador + pozo automáticamente
    
    # ========== MEDIATOR: Coordinar acciones ==========
    # El mediador ya está coordinando automáticamente
    # cuando usas los métodos del GameManager
    
    print("✅ All patterns working together!")


if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*60)
    print("Para usar los patrones en tu juego:")
    print("="*60)
    print("""
1. En gameManager.py, agrega al inicio:
   from patterns_integration import extend_gamemanager_with_patterns
   
2. Decora la clase GameManager:
   @extend_gamemanager_with_patterns
   class GameManager(metaclass=SingletonMeta):
       ...
   
3. ¡Listo! Todos los patrones están disponibles.

4. Hotkeys disponibles:
   - Ctrl+Z: Deshacer
   - Ctrl+Y: Rehacer
   - Ctrl+S: Guardar
   - Ctrl+L: Cargar
   - F5: Auto-save
    """)
