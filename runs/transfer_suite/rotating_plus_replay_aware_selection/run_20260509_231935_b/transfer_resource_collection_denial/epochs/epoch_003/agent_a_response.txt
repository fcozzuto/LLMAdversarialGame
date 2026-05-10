def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2_diag(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obstacle_adj_pen(nx, ny):
        if not obstacles:
            return 0.0
        p = 0.0
        for ax, ay in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in obstacles:
                p += 0.75
        if (nx, ny) in obstacles:
            return 1e6
        return p

    best = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        my_pos = (nx, ny)
        my_best = None
        for rx, ry in resources:
            res = (rx, ry)
            my_d = manh(my_pos, res)
            op_d = manh((ox, oy), res)
            lead = op_d - my_d  # positive if we are closer than opponent
            # Prefer securing resources we can reach sooner, and avoid ones where opponent is much closer
            key = (lead, -my_d)
            if my_best is None or key > my_best:
                my_best = key

        # Convert best key to a single score; include tie-breakers for determinism
        lead, neg_my_d = my_best
        my_d_best = -neg_my_d
        score = (lead * 100.0) - (my_d_best * 1.0) - obstacle_adj_pen(nx, ny)

        # Deterministic tie-break: prefer moves with smaller (dx,dy) lexicographically and then smaller distance to center-ish
        tieb = (score, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2), -my_d_best, dx, dy)
        if best is None or tieb > best:
            best = tieb
            best_move = [dx, dy]

    return best_move