def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        x = y = None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
            elif "x" in p and "y" in p:
                x, y = int(p["x"]), int(p["y"])
        if x is not None and y is not None:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        x = y = None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
            elif "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
        if x is not None and y is not None:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prioritize resources we can reach sooner than the opponent; slight bias to avoid being "late"
    best_r = None
    best_val = 10**18
    for r in resources:
        if (r[0], r[1]) in obstacles:
            continue
        self_d = d((sx, sy), r)
        opp_d = d((ox, oy), r)
        # Lower is better: lead in arrival time + discourage very long detours
        val = (self_d - opp_d) * 10 + self_d + (1 if r[0] == sx or r[1] == sy else 0)
        if val < best_val:
            best_val = val
            best_r = r
    if best_r is None:
        best_r = resources[0]

    tx, ty = best_r
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_best = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Choose move that minimizes distance to target while avoiding stepping into opponent's "sweep" line
        dist_to = d((nx, ny), (tx, ty))
        opp_line = 0
        if ny == oy and abs(nx - ox) <= 2:
            opp_line = 3
        if nx == ox and abs(ny - oy) <= 2:
            opp_line = 3
        val = dist_to + opp_line + (1 if dx == 0 and dy == 0 else 0) * 0.2
        if val < cur_best[0]:
            cur_best = (val, dx, dy)

    # If all candidate next cells were blocked, stay still
    if cur_best[1] == 0 and cur_best[2] == 0:
        return [0, 0]
    return [cur_best[1], cur_best[2]]