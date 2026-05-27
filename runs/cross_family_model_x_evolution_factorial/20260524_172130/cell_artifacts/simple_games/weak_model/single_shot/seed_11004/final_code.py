def choose_move(observation):
    # Defensive access to observation data
    grid = observation.get('grid', [])
    me_pos = observation.get('position', [0, 0])
    resources = observation.get('resources', [])
    enemies = observation.get('enemies', [])
    territory = observation.get('territory', [])
    game_type = observation.get('game_type', '')

    x, y = me_pos

    # Helper to find closest target
    def closest_target(targets):
        min_dist = float('inf')
        target_pos = None
        for t in targets:
            tx, ty = t
            dist = abs(tx - x) + abs(ty - y)
            if dist < min_dist:
                min_dist = dist
                target_pos = (tx, ty)
        return target_pos

    # Initialize move
    dx, dy = 0, 0

    if game_type == 'resource_collection':
        target = closest_target(resources)
        if target:
            tx, ty = target
            dx = (tx - x)
            dy = (ty - y)
        else:
            # No resources visible, move randomly
            dx, dy = 0, 0

    elif game_type == 'pursuit_evasion':
        # If enemy nearby, chase
        enemy_pos = closest_target(enemies)
        if enemy_pos:
            tx, ty = enemy_pos
            dx = (tx - x)
            dy = (ty - y)
        else:
            # No enemy nearby, move randomly
            dx, dy = 0, 0

    elif game_type == 'territory_control':
        # Move towards the center if not there
        # Assume center at (grid width/2, grid height/2)
        if grid:
            height = len(grid)
            width = len(grid[0]) if height > 0 else 0
        else:
            height, width = 0, 0
        center_x, center_y = width // 2, height // 2
        dx = (center_x - x)
        dy = (center_y - y)

    # Clamp dx and dy to -1, 0, 1
    def clamp(n):
        if n > 0:
            return 1
        elif n < 0:
            return -1
        else:
            return 0

    return [clamp(dx), clamp(dy)]
