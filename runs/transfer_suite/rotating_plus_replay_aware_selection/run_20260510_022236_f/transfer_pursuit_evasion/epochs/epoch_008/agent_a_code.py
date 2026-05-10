def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    evade = ("evad" in role) and ("purs" not in role)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0)) % 4
    corner = corners[phase]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # If both agents can reach freely, direct greedy works; obstacles can cause getting stuck, so add simple bias.
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Bias away/toward opponent plus mild corner bias to choose a consistent direction.
        corner2 = (nx - corner[0]) * (nx - corner[0]) + (ny - corner[1]) * (ny - corner[1])

        # Obstacle-aware local openness: count free neighbors to reduce collisions.
        open_cnt = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if ok(tx, ty):
                    open_cnt += 1

        if evade:
            # Maximize distance; prefer more open space; also break ties by preferring corner direction alternating.
            val = dist2 * 100 + open_cnt * 3 + (-corner2 if phase % 2 == 0 else corner2) * 0.01
        else:
            # Minimize distance; prefer more open space; consistent corner pressure.
            val = -dist2 * 100 + open_cnt * 3 + (corner2 if phase % 2 == 0 else -corner2) * 0.01

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]