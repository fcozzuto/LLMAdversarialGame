def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_raw = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))

    if not rpos:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev

    # Pick a resource where we are meaningfully closer than opponent (denial-aware).
    best_r = None
    best_val = -10**9
    for rx, ry in rpos:
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        # Prefer resources we can reach first; tie-break toward center and slight obstacle-free bias.
        val = (d2 - d1) * 10 - d1
        val += -0.01 * (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    rx, ry = best_r

    # Obstacle-aware greedy step to reduce our distance to chosen target.
    cur_d = dist((sx, sy), (rx, ry))
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nd = dist((nx, ny), (rx, ry))
        # also discourage stepping into opponent's immediate range (resource-denial counterplay)
        opp_next = dist((nx, ny), (ox, oy))
        candidates.append((nd, -opp_next, dx, dy))
    if not candidates:
        return [0, 0]

    # Choose minimal distance, then maximize distance-from-opponent.
    candidates.sort()
    nd, _, dx, dy = candidates[0]
    # If no improvement, allow staying or the least-bad move (still deterministic).
    if nd > cur_d:
        for nd2, _, dx2, dy2 in candidates:
            if nd2 == min(c[0] for c in candidates):
                return [dx2, dy2]
        return [0, 0]
    return [dx, dy]