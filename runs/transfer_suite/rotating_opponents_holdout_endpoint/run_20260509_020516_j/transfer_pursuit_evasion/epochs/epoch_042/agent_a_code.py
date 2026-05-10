def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("catcher" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def corner_bias(x, y):
        best = 0
        for cx, cy in corners:
            best = max(best, abs(cx - ox) + abs(cy - oy) - (abs(cx - x) + abs(cy - y)))
        return best

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d_now = dist(sx, sy)
        d_new = dist(nx, ny)

        # Anticipate opponent next by considering our move relative to their current position:
        # For pursuer: minimize distance; for evader: maximize distance.
        if is_pursuer:
            score = -d_new * 10 + (d_now - d_new) * 3
            # Prefer moves that don't allow an immediate "stay closer" for opponent, approximated by avoiding staying in same manhattan band.
            score += (1 if d_new <= d_now else -1)
            # Mildly avoid corners where opponent might slip around obstacles less safely (generic).
            score -= corner_bias(nx, ny) * 0.05
        else:
            score = d_new * 10 + (d_new - d_now) * 3
            # Strongly prefer moving toward a far corner relative to the opponent.
            target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            tx, ty = target_corner
            score += (abs(tx - nx) + abs(ty - ny)) * 1.5
            # Avoid getting boxed: prefer having at least one legal neighbor after move.
            deg = 0
            for ddx, ddy in moves:
                xx, yy = nx + ddx, ny + ddy
                if legal(xx, yy):
                    deg += 1
            score += deg * 0.7

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]