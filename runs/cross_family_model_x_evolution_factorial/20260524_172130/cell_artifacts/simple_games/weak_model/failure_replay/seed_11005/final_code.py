def choose_move(observation):
    gw = observation.get('grid_width', 1)
    gh = observation.get('grid_height', 1)
    px, py = observation.get('self_position', (0, 0))
    ox, oy = observation.get('opponent_position', (0, 0))
    resources = observation.get('resources', [])
    obstacles = observation.get('obstacles', [])
    attack_mode = observation.get('attack_mode', False)

    def move_towards(tx, ty):
        dx, dy = 0, 0
        if tx > px:
            dx = 1
        elif tx < px:
            dx = -1
        if ty > py:
            dy = 1
        elif ty < py:
            dy = -1
        return dx, dy

    def is_blocked(nx, ny):
        if nx < 0 or nx >= gw or ny < 0 or ny >= gh:
            return True
        if (nx, ny) in obstacles:
            return True
        return False

    def try_move(dx, dy):
        nx, ny = px + dx, py + dy
        if not is_blocked(nx, ny):
            return [dx, dy]
        return None

    # Attack if opponent adjacent
    if attack_mode:
        dx, dy = move_towards(ox, oy)
        move = try_move(dx, dy)
        if move:
            return move
        else:
            for ddx, ddy in [(-1,0), (1,0), (0,-1), (0,1)]:
                move = try_move(ddx, ddy)
                if move:
                    return move
        return [0, 0]

    # Prioritize resource collection
    resource_moves = []
    for rx, ry in resources:
        dx, dy = move_towards(rx, ry)
        move = try_move(dx, dy)
        if move:
            resource_moves.append((abs(rx - px) + abs(ry - py), move))
    if resource_moves:
        _, best_move = min(resource_moves, key=lambda x: x[0])
        return best_move

    # Move towards opponent for defense
    dx, dy = move_towards(ox, oy)
    move = try_move(dx, dy)
    if move:
        return move

    # Try all directions
    for ddx, ddy in [(-1,0), (1,0), (0,-1), (0,1)]:
        move = try_move(ddx, ddy)
        if move:
            return move

    # Stay still if no move
    return [0, 0]
