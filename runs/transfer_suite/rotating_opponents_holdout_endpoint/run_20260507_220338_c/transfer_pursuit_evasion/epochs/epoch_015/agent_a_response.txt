def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_move(nx, ny):
        dx = nx - ox
        dy = ny - oy
        dist2 = dx * dx + dy * dy

        # Ambush toward the edge opponent is "closer to"
        edge_x = 0 if ox <= (w - 1) // 2 else w - 1
        edge_y = 0 if oy <= (h - 1) // 2 else h - 1
        # Encourage approaching the nearer of the two edges: both coordinates matter for diagonal zigzags
        edge_dist = min(abs(nx - edge_x) + abs(ny - oy), abs(nx - ox) + abs(ny - edge_y))

        # Parity bias to counter zigzag alternation
        parity_bonus = 1.0 if ((nx + ny) & 1) == ((ox + oy) & 1) else 0.0

        # Mobility (avoid getting boxed)
        mobility = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if in_bounds(tx, ty) and (tx, ty) not in blocked:
                mobility += 1

        if pursuer:
            return -dist2 + 0.20 * mobility - 0.03 * edge_dist + 0.10 * parity_bonus
        else:
            return dist2 - 0.20 * mobility + 0.03 * edge_dist + 0.10 * parity_bonus

    best_move = (0, 0)
    best_val = None
    sign = -1 if pursuer else 1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue
        val = score_move(nx, ny)
        if best_val is None or sign * val > sign * best_val or (sign * val == sign * best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]