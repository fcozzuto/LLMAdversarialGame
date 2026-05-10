def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in self_role) or ("pursuer" in opp_role and "evader" in self_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    neigh4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def free_count(x, y):
        c = 0
        for dx, dy in neigh4:
            nx, ny = x + dx, y + dy
            if free(nx, ny):
                c += 1
        return c

    best_move = moves[0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        fc = free_count(nx, ny)
        # Small bias to avoid corners/edges for evader and to take open lanes for pursuer
        edge_pen = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)

        if self_is_evader:
            # Evader: maximize distance, prefer openness, avoid edges.
            score = (d2 * 1.0) + (2.2 * fc) - (1.1 * edge_pen)
        else:
            # Pursuer: minimize distance, prefer moving into open space.
            score = (-d2 * 1.0) + (1.4 * fc) - (0.4 * edge_pen)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move