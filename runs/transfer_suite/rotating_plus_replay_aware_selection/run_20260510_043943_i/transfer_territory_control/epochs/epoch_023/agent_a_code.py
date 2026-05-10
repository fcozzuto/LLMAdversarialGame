def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_terr = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    targets = []
    for key in ("resources", "unclaimed_cells"):
        v = observation.get(key, None)
        if isinstance(v, list) and v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    targets.append((int(p[0]), int(p[1])))
            if targets:
                break

    if not targets:
        # if no unclaimed/resource info, chase opponent territory to counterclaim
        for p in observation.get("opponent_territory", []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))

    # simple deterministic "territory pressure": move toward best target;
    # if stepping into opponent territory, prioritize it strongly.
    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        step_into_opp = 1 if (nx, ny) in opp_terr else 0
        if targets:
            d = min(man(nx, ny, tx, ty) for tx, ty in targets)
        else:
            d = 0

        # Prefer: winning pressure (opp territory), then closeness, then avoid staying still when possible.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        key = (-step_into_opp, d, stay_pen, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move