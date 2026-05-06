def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not rpos:
        # fallback: move away from opponent to reduce denials
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            v = dist(nx, ny, ox, oy)
            if v > best[1]:
                best = ((dx, dy), v)
        return [best[0][0], best[0][1]] if best[0] else [0, 0]

    best_r = None
    best_v = -10**18
    for rx, ry in rpos:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer resources where we are relatively closer than opponent, still somewhat close to us.
        v = (do - ds) * 10 - ds
        if v > best_v:
            best_v = v
            best_r = (rx, ry)

    tx, ty = best_r
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        cand.append((dx, dy, dist(nx, ny, tx, ty), dist(nx, ny, ox, oy)))
    if cand:
        # Tie-break: avoid stepping into opponent proximity.
        cand.sort(key=lambda t: (t[2], -t[3]))
        dx, dy = cand[0][0], cand[0][1]
        return [dx, dy]
    return [0, 0]