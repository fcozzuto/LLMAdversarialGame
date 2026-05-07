def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        da = ax - bx
        db = ay - by
        return da if da >= 0 else -da if da != 0 else (db if db >= 0 else -db)

    if res:
        best = None
        best_score = None
        for tx, ty in res:
            sd = max(abs(sx - tx), abs(sy - ty))
            od = max(abs(ox - tx), abs(oy - ty))
            # Prefer reachable soon and where opponent is later; small bias to breaking ties closer.
            score = (od - sd, -sd)
            if best is None or score > best_score:
                best = (tx, ty)
                best_score = score
        tx, ty = best
    else:
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        dist = max(abs(nx - tx), abs(ny - ty))
        opp_dist = max(abs(ox - tx), abs(oy - ty))
        # Minimize distance to target; if tie, prefer moves that keep farther from target for opponent not possible -> just keep closer.
        val = (dist, -opp_dist, dx == 0 and dy == 0)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]