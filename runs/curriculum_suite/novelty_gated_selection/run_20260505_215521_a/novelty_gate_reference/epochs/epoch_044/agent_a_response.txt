def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    # Resource denial adaptation: prefer resources where opponent is not closer.
    best = None
    bestv = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Consider only up to 6 closest resources to keep deterministic/fast
        cand = []
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            cand.append((ds, do, rx, ry))
        cand.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
        cand = cand[:6] if cand else [(0, 0, sx, sy)]
        v = 10**18
        for ds, do, rx, ry in cand:
            closer_pen = 0
            if do < ds:
                closer_pen = 5 + (ds - do)  # likely to be denied
            elif do == ds:
                closer_pen = 2
            # Also discourage walking into opponent proximity unless we can secure a resource immediately.
            opp_adj = md(nx, ny, ox, oy)
            prox_pen = 0
            if opp_adj <= 2:
                prox_pen = 2 if (ds > 0) else 0
            val = ds + closer_pen + prox_pen + 0.01 * do
            if val < v:
                v = val
        # Tie-break deterministically toward staying closer to resources and away from opponent
        if v < bestv or (v == bestv and md(nx, ny, ox, oy) > (md(sx, sy, ox, oy)) and (dx, dy) < (best[0], best[1]) if best else False):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]