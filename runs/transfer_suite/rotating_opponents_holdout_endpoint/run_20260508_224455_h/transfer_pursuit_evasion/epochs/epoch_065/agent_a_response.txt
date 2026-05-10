def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            if isinstance(p, dict) and "x" in p and "y" in p:
                x, y = int(p["x"]), int(p["y"])
            else:
                continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    role = str(observation.get("self_role") or observation.get("role") or "").lower()
    evader = ("evader" in role) or ("escape" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Prefer moves that increase/decrease distance to the opponent while avoiding obstacles.
    best = None
    best_score = None

    # Deterministic tie-break: prefer diagonal only if it helps; otherwise prefer axis moves.
    def tie_key(dx, dy):
        diag = 1 if (dx != 0 and dy != 0) else 0
        stay = 1 if (dx == 0 and dy == 0) else 0
        return (diag, stay, dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # Small bias to avoid staying still.
        stay_bias = -0.01 if (dx == 0 and dy == 0) else 0.0
        if evader:
            score = d + stay_bias
            better = (best_score is None) or (score > best_score) or (score == best_score and tie_key(dx, dy) < tie_key(best[0], best[1]) if best is not None else False)
        else:
            score = -d + stay_bias
            better = (best_score is None) or (score > best_score) or (score == best_score and tie_key(dx, dy) < tie_key(best[0], best[1]) if best is not None else False)
        if better:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    # Fallback: if all moves invalid (rare), stay.
    return [0, 0]