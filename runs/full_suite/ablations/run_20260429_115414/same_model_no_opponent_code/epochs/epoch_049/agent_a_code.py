def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inside = lambda x, y: 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_dist(startx, starty, limit):
        if (startx, starty) in obstacles:
            return 10**9
        qx = [startx]
        qy = [starty]
        qd = [0]
        head = 0
        seen = {(startx, starty): 0}
        best = 10**9
        resset = set(resources)
        while head < len(qx):
            x, y, d = qx[head], qy[head], qd[head]
            head += 1
            if d > limit:
                continue
            if (x, y) in resset:
                if d < best:
                    best = d
                    if best == 0:
                        return 0
            if d == limit:
                continue
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                nd = d + 1
                if inside(nx, ny) and (nx, ny) not in seen:
                    seen[(nx, ny)] = nd
                    qx.append(nx)
                    qy.append(ny)
                    qd.append(nd)
        return best

    opp_dist = best_dist(ox, oy, 8)
    def score_for_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
        d_ours = best_dist(nx, ny, 8)
        if d_ours >= 10**8:
            return 10**9
        # Prefer moves that both reduce our distance and (when possible) prevent opponent from being closer.
        # Tie-break toward moving toward opponent side by projection.
        closer_pressure = d_ours - int(opp_dist * 0.85)
        proj = abs((nx - ox)) + abs((ny - oy))
        return closer_pressure * 1000 + proj

    best = None
    best_val = 10**18
    # Deterministic tie-break order: dirs list order already deterministic.
    for dx, dy in dirs:
        v = score_for_move(dx, dy)
        if v < best_val:
            best_val = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]