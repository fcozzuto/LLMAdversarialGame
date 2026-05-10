def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = observation.get("self_role", "pursuer")
    is_pursuer = (self_role == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    vx, vy = sx - ox, sy - oy  # direction away from opponent (sign flips for pursuer)
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        nd = d2(nx, ny, ox, oy)
        if is_pursuer:
            # Greedy chase; prefer moves that reduce distance, also break ties by projecting along vector to opponent.
            score = -nd
            score += 0.01 * (nx - sx) * (ox - sx) + 0.01 * (ny - sy) * (oy - sy)
            # If tie, prefer staying closer to center to avoid getting trapped.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score -= 0.0005 * d2(nx, ny, cx, cy)
        else:
            # Evasion: maximize distance, and keep moving generally away; also discourage stepping next to obstacles too aggressively.
            score = nd
            score += 0.02 * (nx - sx) * vx + 0.02 * (ny - sy) * vy
            # Prefer moves toward the farthest corner when distances tie.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            fc = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            score += 0.001 * (abs(nx - fc[0]) + abs(ny - fc[1]))
            # Mild obstacle penalty: fewer legal neighbors preferred to avoid oscillations near tight corridors.
            neigh = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if legal(tx, ty):
                    neigh += 1
            score += 0.005 * (-neigh)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]