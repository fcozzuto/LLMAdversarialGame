def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evad" in role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # If evader: aim for the corner farthest from pursuer; else aim for the evader's position.
    if is_evader:
        tx, ty = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
        def primary(x, y):  # maximize distance to opponent, with secondary goal toward target corner
            return (dist2(x, y), -((tx - x) * (tx - x) + (ty - y) * (ty - y)))
        prefer = -1
    else:
        tx, ty = ox, oy
        def primary(x, y):  # minimize distance to opponent, with secondary goal toward x,y target
            return (-dist2(x, y), -((tx - x) * (tx - x) + (ty - y) * (ty - y)))
        prefer = 1

    best_move = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Obstacle-aware: penalize stepping into "tight" cells by counting available neighbors
        free_n = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                free_n += 1

        corner_edge = min(nx, w - 1 - nx, ny, h - 1 - ny)  # prefer staying away from borders when chasing
        key = primary(nx, ny)
        # Tie-break: fewer neighbors is bad; if pursuer, also prefer lower edge distance (closer to center isn't required)
        key = (key, -free_n, (edge_bias if (edge_bias := corner_edge) is not None else 0))
        if best_key is None or (key[0][0] * prefer > best_key[0][0] * prefer):
            best_key = key
            best_move = [dx, dy]
        elif best_key is not None:
            # deterministic lexicographic refinement
            if key > best_key:
                best_key = key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]