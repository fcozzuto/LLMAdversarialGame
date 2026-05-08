def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None:
            obst.add((p[0], p[1]))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Resource race heuristic: prefer moves that make us closer than opponent
        best_resource_val = None
        best_resource_dist = None
        for rx, ry in resources:
            my_d = max(abs(nx - rx), abs(ny - ry))
            op_d = max(abs(ox - rx), abs(oy - ry))
            # Higher is better: advantage in reaching the same resource
            val = (op_d - my_d) * 2.0 - my_d
            if best_resource_val is None or val > best_resource_val or (val == best_resource_val and my_d < best_resource_dist):
                best_resource_val = val
                best_resource_dist = my_d

        # Small penalty for staying still
        stay_pen = 0.35 if (dx == 0 and dy == 0) else 0.0
        move_val = best_resource_val - stay_pen

        if best_val is None or move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]