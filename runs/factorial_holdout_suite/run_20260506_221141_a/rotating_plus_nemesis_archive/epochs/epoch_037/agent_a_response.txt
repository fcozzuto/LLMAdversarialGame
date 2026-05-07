def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                obs.add((x, y))

    if not (isinstance(sx, int) and isinstance(sy, int) and inb(sx, sy)):
        return [0, 0]
    if not (isinstance(ox, int) and isinstance(oy, int) and inb(ox, oy)):
        ox, oy = w - 1, h - 1

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))
    if not rlist:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = None
    best_val = None
    # Prefer immediate capture; otherwise choose step that maximizes "self advantage" over opponent
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        step_val = -10**9
        if (nx, ny) in rlist:
            step_val = 10**9  # immediate collection dominates
        else:
            for rx, ry in rlist:
                sd = dist((nx, ny), (rx, ry))
                od = dist((ox, oy), (rx, ry))
                adv = od - sd  # positive means we reach sooner
                # break ties toward nearer resources, then toward reducing distance to opponent (shadow defense)
                val = adv * 1000 - sd - (abs(nx - ox) + abs(ny - oy)) // 2
                if val > step_val:
                    step_val = val
        if best_val is None or step_val > best_val or (step_val == best_val and (dx, dy) < best_move):
            best_val = step_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]