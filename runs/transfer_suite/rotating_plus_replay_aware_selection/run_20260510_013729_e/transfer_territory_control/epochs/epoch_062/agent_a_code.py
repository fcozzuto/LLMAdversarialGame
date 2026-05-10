def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = set()
    if self_t and unclaimed:
        for (tx, ty) in self_t:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = tx + dx, ty + dy
                    if (nx, ny) in unclaimed:
                        targets.add((nx, ny))

    if not targets:
        targets = unclaimed if unclaimed else set()

    if not targets:
        targets = set(resources) if resources else {((w - 1) // 2, (h - 1) // 2)}

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not targets:
        tx, ty = cx, cy
    else:
        tx, ty = min(targets, key=lambda t: (abs(t[0] - x) + abs(t[1] - y), abs(t[0] - cx) + abs(t[1] - cy), t[0], t[1]))

    best = (10**9, 10**9, 10**9, 10**9)
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        border = 0
        if (nx, ny) in unclaimed:
            border -= 6
        if (nx, ny) in opp_t:
            border -= 3
        opp_d = abs(nx - ox) + abs(ny - oy)
        cand = (d + (0 if border else 0), -border, opp_d, nx * 10 + ny)
        if cand < best:
            best = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]