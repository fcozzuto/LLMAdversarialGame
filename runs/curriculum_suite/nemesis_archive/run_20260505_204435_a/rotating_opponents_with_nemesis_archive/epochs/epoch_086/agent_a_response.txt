def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (int(r[0]), int(r[1]))
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (int(q[0]), int(q[1]))
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # Choose a resource where we have strongest distance advantage over opponent
    best_res = None
    best_adv = -10**9
    for (rx, ry) in sorted(rpos):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = (do - ds)  # higher means we are closer than opponent
        # Tie-break: prefer nearer resources to reduce time
        key = (adv, -ds, rx, ry)
        if best_res is None or key > best_adv:
            best_adv = key
            best_res = (rx, ry)

    rx, ry = best_res

    # Move toward chosen resource, but avoid stepping into obstacle; also keep opponent pressure low
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(nx, ny, ox, oy)
        # Prefer reducing our distance, and also not giving the opponent immediate capture leverage
        val = (-ds2) + 0.08 * do2
        # Small deterministic tie-break to avoid oscillation
        val += -0.001 * (abs(dx) + abs(dy))
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move