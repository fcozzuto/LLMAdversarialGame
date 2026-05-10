def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in blocked:
                    res.append((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "escape", "runner", "flee", "defender"))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    best = None
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dres = min((man(nx, ny, rx, ry) for (rx, ry) in res), default=0)
        dop = man(nx, ny, ox, oy)
        # Prefer resources; add opposite pressure depending on role.
        v = 1000 * (-dres) + (dop if is_evader else -dop)
        # Tiny deterministic tie-breaker: prefer staying closer to center of grid.
        v += - (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.01
        if v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best