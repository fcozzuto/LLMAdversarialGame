def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) or ("catch" in self_role) or ("hunter" in self_role)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def free(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best_move = (0, 0)
    best_score = None
    # Deterministic tie-break ordering prefers staying still less.
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue

        dist_to_opp = cheb(nx, ny, ox, oy)

        # Mobility: count free neighbors after the move (avoid dead-ends).
        mob = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if free(tx, ty):
                mob += 1

        # Corner bias to break symmetry for evasion-wall-runner: move toward opposite corner when evading,
        # and toward closer corner when pursuing (helps avoid oscillations around obstacles).
        corner_dist = cheb(nx, ny, target_corner[0], target_corner[1])
        corner_bias = -corner_dist if not pursuer else corner_dist

        # Composite score
        # - Pursuer: minimize distance, but keep mobility and avoid getting stuck.
        # - Evader: maximize distance and also keep mobility high.
        score = (dist_to_opp * (-1 if pursuer else 1)) + (mob * (0.12 if pursuer else 0.18)) + (corner_bias * 0.05)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]