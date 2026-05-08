def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("tag" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def step_cost(nx, ny):
        # discourage obstacles and edges (prefer safe lanes)
        c = 0.0
        if (nx, ny) in obst:
            c += 100000.0
        c += (nx < 1 or nx > w - 2) * 2.0
        c += (ny < 1 or ny > h - 2) * 2.0
        # also encourage staying away from obstacles
        if obst:
            best = 10**9
            for bx, by in obst:
                d = dist2(nx, ny, bx, by)
                if d < best:
                    best = d
            if best < 16:
                c += (16.0 - best) * 20.0
        return c

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        d = dist2(nx, ny, ox, oy)
        cost = step_cost(nx, ny)
        val = (-d - cost) if is_pursuer else (d - cost)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move