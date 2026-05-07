def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if (sx, sy) in set(resources):
        return [0, 0]

    # Pick a resource we can reach sooner than the opponent, else pick best denial race.
    best = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        adv = od - sd
        # Deterministic tie-break: prefer smaller self distance, then lexicographic.
        key = (adv, -sd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Greedy step toward target, but keep deterministic tie-break.
    best_step = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = abs(tx - nx) + abs(ty - ny)
        # If multiple steps are equally good, prefer one that also increases (opp dist - self dist) locally.
        oppd = abs(tx - ox) + abs(ty - oy)
        selfd = abs(tx - nx) + abs(ty - ny)
        local_adv = oppd - selfd
        key = (-d, local_adv, -nx, -ny)
        if best_step is None or key > best_step[0]:
            best_step = (key, (dx, dy))
    return [int(best_step[1][0]), int(best_step[1][1])]