def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
    res_set = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = (-10**18, 0, 0)

    # If we can take immediately, do it with a denial-aware tie-break.
    immediate = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in res_set:
            opp_d = min((md((nx, ny), (rx, ry)) for rx, ry in resources), default=0)
            immediate.append((-(opp_d), -(nx + ny), dx, dy))
    if immediate:
        immediate.sort()
        _, _, dx, dy = immediate[0]
        return [int(dx), int(dy)]

    # Otherwise: maximize opponent's pressure while improving ours.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_best = min((md((nx, ny), (rx, ry)) for rx, ry in resources), default=10**9)
        # Opponent is expected to chase the nearest remaining resource; deny by increasing that distance.
        opp_best = min((md((ox, oy), (rx, ry)) for rx, ry in resources), default=10**9)

        # Heuristic: prefer moves that reduce our distance, and (more importantly) reduce resources that are closer to opponent.
        # Use (opp_best - self_best) as main driver, with deterministic tie-break on coordinates.
        denom = 1 + self_best + opp_best
        gain = (opp_best - self_best) * 1000 - (self_best + 2 * (nx + ny)) / denom
        cand = (gain, -self_best, -(nx + ny), dx, dy)
        if cand > best:
            best = cand

    _, _, _, bdx, bdy = best
    return [int(bdx), int(bdy)]