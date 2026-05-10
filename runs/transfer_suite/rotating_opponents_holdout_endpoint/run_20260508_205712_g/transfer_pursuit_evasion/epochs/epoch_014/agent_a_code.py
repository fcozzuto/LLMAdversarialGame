def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obstacles.add((int(a[0]), int(a[1])))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h
    def ok(x, y): 
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role)

    # Evader tends to a farthest corner; pursuer tends to directly chase.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    tx, ty = (ox, oy) if pursuer else (far_corner[0], far_corner[1])

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_to_target = abs(nx - tx) + abs(ny - ty)

        # Simple obstacle-aware pressure: penalize moves that get "boxed" (low mobility).
        mobility = 0
        for ddx, ddy in moves:
            x2, y2 = nx + ddx, ny + ddy
            if ok(x2, y2):
                mobility += 1

        # Pointers:
        # - pursuer minimizes distance to opponent
        # - evader maximizes distance from opponent / target corner
        if pursuer:
            val = (d_to_target, -mobility, dx, dy)
            if best is None or val < best_val:
                best, best_val = (dx, dy), val
        else:
            val = (-d_to_target, -mobility, dx, dy)
            if best is None or val < best_val:
                best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]