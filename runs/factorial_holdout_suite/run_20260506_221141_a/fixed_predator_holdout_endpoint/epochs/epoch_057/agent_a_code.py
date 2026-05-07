def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                resources.append((x, y))
        except Exception:
            pass
    if not resources:
        return [0, 0]

    def kd(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = abs(ax - bx), abs(ay - by)
        return dx if dx > dy else dy

    # Pick a good race target deterministically.
    best_t, best_key = None, None
    for t in resources:
        sd = kd((sx, sy), t)
        od = kd((ox, oy), t)
        key = (od - sd, -sd, t[0], t[1])
        if best_key is None or key > best_key:
            best_key, best_t = key, t

    tx, ty = best_t

    # Try legal moves and maximize race advantage after the move.
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def eval_cell(x, y):
        if (x, y) in obs_set:
            return (-10**9, -10**9)
        sd = kd((x, y), (tx, ty))
        od = kd((ox, oy), (tx, ty))
        return (od - sd, -sd)

    best_m, best_v = (0, 0), None
    # Deterministic tie-break: prefer smaller dx then smaller dy, then closer-to-target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            v = eval_cell(nx, ny)
            if best_v is None or v > best_v or (v == best_v and (dx, dy) < best_m):
                best_v, best_m = v, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]