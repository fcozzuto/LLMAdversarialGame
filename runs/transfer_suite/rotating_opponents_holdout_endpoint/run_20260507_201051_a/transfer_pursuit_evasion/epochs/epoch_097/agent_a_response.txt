def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    pursuer = any(k in role for k in ("purs", "hunt", "chaser", "seeker", "hunter", "pursuer", "catch", "catcher"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dxdy = moves[4]
    best_val = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def adj_obst(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    c += 1
        return c

    def near_op_block(x, y):
        return dist2(x, y, ox, oy) <= 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        ao = adj_obst(nx, ny)
        stay = 1 if (dx == 0 and dy == 0) else 0
        # Deterministic tie-break: prefer lexicographically smaller (dx,dy) via score then (dx,dy)
        val = (d, ao, stay, 0 if near_op_block(nx, ny) else 1)
        if pursuer:
            # minimize distance, then avoid obstacles
            key = (d * 1000 + ao * 10 + stay, dx, dy)
            better = (best_val is None) or (key < best_val)
        else:
            # maximize distance, then avoid obstacles
            key = (-d * 1000 + ao * 10 + stay, dx, dy)
            better = (best_val is None) or (key < best_val)
        if better:
            best_val = key
            best_dxdy = [dx, dy]

    return best_dxdy if best_dxdy in [list(m) for m in moves] else [0, 0]