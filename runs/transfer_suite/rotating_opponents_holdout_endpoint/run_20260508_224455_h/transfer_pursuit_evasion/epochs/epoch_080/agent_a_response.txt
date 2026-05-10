def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    sr = (observation.get("self_role") or "").lower()
    pr = "purs" in sr

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    # If pursuer: minimize distance; if evader: maximize distance. Tie-breaker: pref moves order above.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        score = -d if pr else d
        if best is None or score > best[0]:
            best = (score, dx, dy)
        elif score == best[0]:
            if (dx, dy) == moves[0]:
                best = (score, dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]