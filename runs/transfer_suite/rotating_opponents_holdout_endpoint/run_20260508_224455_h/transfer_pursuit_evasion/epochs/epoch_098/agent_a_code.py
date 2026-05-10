def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    want_evade = role in ("evader", "evading", "runner")

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        ax = dx if dx >= 0 else -dx
        ay = dy if dy >= 0 else -dy
        return ax if ax >= ay else ay

    def score(nx, ny):
        d = cheb(nx, ny, ox, oy)
        md = abs(nx - ox) + abs(ny - oy)
        if want_evade:
            # Prefer staying away, and avoid moving into tight corridors near obstacles.
            corner_boost = max(0, (nx in (0, w - 1)) + (ny in (0, h - 1)))
            return (d, md, corner_boost)
        else:
            # Pursue by reducing both Chebyshev and Manhattan; also try to "shadow" opponent direction.
            dir_align = (1 if (nx - sx) * (ox - sx) >= 0 else -1) + (1 if (ny - sy) * (oy - sy) >= 0 else -1)
            return (-d, -md, dir_align)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        k = score(nx, ny)
        if best_key is None:
            best_key, best = k, (dx, dy)
        else:
            if want_evade:
                if k > best_key:
                    best_key, best = k, (dx, dy)
            else:
                if k > best_key:
                    best_key, best = k, (dx, dy)

    return [int(best[0]), int(best[1])]