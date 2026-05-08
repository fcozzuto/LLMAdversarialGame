def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def mobility(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("flee" in role) or ("evade" in role)

    # Prefer moves that keep options open and push relative distance in the right direction.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)
        dead_pen = 0 if mob >= 2 else (6 if mob == 1 else 20)

        if evader:
            # Run away from pursuer; avoid getting trapped in low-mobility cells.
            score = (dist * 10) + (mob * 2) - dead_pen
        else:
            # Pursue: minimize distance primarily, avoid dead ends, and slightly prefer higher mobility.
            score = (-dist * 10) + (mob) - dead_pen

        # Deterministic tie-break: lexicographic by (score, -dist/x/y) implicitly using total key.
        key = (score, -dist if evader else dist, mob, -nx, -ny)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]