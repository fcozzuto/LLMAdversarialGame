def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def sqd(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    resources = observation.get("resources") or []
    best = None
    bestd = None
    for r in resources:
        try:
            if isinstance(r, dict):
                x, y = int(r.get("x")), int(r.get("y"))
            else:
                x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                d = sqd(x, y, sx, sy)
                if bestd is None or d < bestd:
                    bestd = d
                    best = (x, y)
        except Exception:
            pass

    role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in role) or ("hun" in role) or ("pred" in role) or (role == "pursuer")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Base heuristic: go to nearest resource; otherwise, chase/avoid opponent deterministically.
        if best is not None:
            score = -sqd(nx, ny, best[0], best[1])
        else:
            score = (sqd(nx, ny, ox, oy) if not pursuer else -sqd(nx, ny, ox, oy))
        # Small tie-break: prefer staying within bounds and not getting adjacent to obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obs:
                    adj += 1
        score -= adj * 0.01
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]