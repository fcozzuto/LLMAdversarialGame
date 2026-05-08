def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    opp_terr = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    dirs.sort()

    # Pick a target cell to counterclaim: nearest opponent territory if any, else nearest unclaimed.
    if opp_terr:
        targets = list(opp_terr)
    else:
        targets = list(unclaimed)
    if not targets:
        return [0, 0]
    targets.sort(key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - ox) + abs(t[1] - oy), t[0], t[1]))
    tx, ty = targets[0]

    def step_valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def score_cell(nx, ny):
        cell = (nx, ny)
        # Primary: counterclaim tendency (enter opponent territory is valuable).
        s = 0
        if cell in opp_terr:
            s += 10000
        if cell in unclaimed:
            s += 200
        # Second: approach target.
        s -= 10 * (abs(nx - tx) + abs(ny - ty))
        # Third: prefer cells adjacent to opponent territory (increase odds of flips next turns).
        adj = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in opp_terr:
                    adj += 1
        s += 30 * adj
        # Mild repulsion from our current position not needed; keep deterministic by tie-breaking on coords.
        s += -0.01 * ((nx - sx) ** 2 + (ny - sy) ** 2)
        return s

    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not step_valid(nx, ny):
            continue
        sc = score_cell(nx, ny)
        key = (sc, -dx, -dy)  # deterministic tie-break favoring earlier dirs in sorted order
        if key > best:
            best = key
    # If all moves blocked, stay.
    dx = best[1] if best[1] in (-1, 0, 1) else 0
    dy = best[2] if best[2] in (-1, 0, 1) else 0
    return [dx, dy]