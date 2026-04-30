def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            pos = None
            if "pos" in r:
                pos = r.get("pos")
            x = r.get("x", None)
            y = r.get("y", None)
            if pos is not None and isinstance(pos, (list, tuple)) and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            elif x is not None and y is not None:
                resources.append((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]
    resources = [rp for rp in resources if 0 <= rp[0] < w and 0 <= rp[1] < h]
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # pick the resource where this move creates the biggest lead vs the opponent (approx).
        v = 0
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            lead = d_opp - d_self  # positive if we get closer than opponent
            # prefer near-term contest and avoid overcommitting far away
            v = max(v, lead * 10 - d_self)
        # slight bias toward moving toward the currently best target (greedy stability)
        if v > bestv or (v == bestv and (dx, dy) == (0, 0)):
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]