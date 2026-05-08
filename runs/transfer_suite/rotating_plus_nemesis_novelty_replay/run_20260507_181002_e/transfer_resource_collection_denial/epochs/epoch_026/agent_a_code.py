def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Step 1: pick a stealable resource (we arrive earlier), else contest opponent's nearest.
    best = None
    best_key = None
    for cell in res:
        sd = man((sx, sy), cell)
        od = man((ox, oy), cell)
        # Prefer arriving earlier; if none, minimize opponent arrival.
        if sd < od:
            margin = (od - sd)
            key = (0, -margin, sd, cell[0], cell[1])
        else:
            key = (1, od, sd, cell[0], cell[1])
        if best_key is None or key < best_key:
            best_key, best = key, cell

    tx, ty = best

    # Step 2: move to the neighbor that most improves our odds for the chosen target.
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    cur = (sx, sy)
    cur_sd = man(cur, (tx, ty))
    opp_td = man((ox, oy), (tx, ty))

    chosen = (0, 0)
    chosen_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nsd = man((nx, ny), (tx, ty))
        # If we can potentially beat opponent arrival, prioritize that.
        before = (opp_td - nsd)
        key = (-1 if valid(nx, ny) else 0, abs(nx - tx) + abs(ny - ty), -before, nx, ny, dx, dy)
        # Actually key wants smaller: use a combined ordering.
        key = (0 if before > 0 else 1, abs(nx - tx) + abs(ny - ty), -before, nx, ny)
        if chosen_key is None or key < chosen_key:
            chosen_key, chosen = key, (dx, dy)

    return [int(chosen[0]), int(chosen[1])]