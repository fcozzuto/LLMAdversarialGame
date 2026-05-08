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

    self_terr = set(tuple(p) for p in observation.get("self_territory", []) or [])
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory", []) or [])
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        t = a - c
        if t < 0: t = -t
        u = b - d
        if u < 0: u = -u
        return t + u

    # Target selection: prioritize nearby unclaimed around our frontier; else center; else unclaimed anywhere.
    if self_terr:
        frontier = set()
        for (x, y) in self_terr:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
        cand = list(frontier) if frontier else list(unclaimed)
    else:
        cand = list(unclaimed)

    if cand:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        # Bias toward center + away from opponent.
        best = None
        bestd = 10**18
        for x, y in cand:
            d = man(x, y, sx, sy) * 2 + man(x, y, ox, oy)
            dc = abs(x - cx) + abs(y - cy)
            score = d + int(dc * 0.5)
            if score < bestd:
                bestd = score
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = int((w - 1) / 2), int((h - 1) / 2)

    # Evaluate immediate moves with territory outcome.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0
        if (nx, ny) in opp_terr:
            val += 8
        elif (nx, ny) in unclaimed:
            val += 4
        elif (nx, ny) in self_terr:
            val += 1

        # Distance shaping: go toward target, but also avoid walking into opponent territory too slowly.
        val -= man(nx, ny, tx, ty)
        val -= 0.5 * man(nx, ny, ox, oy) if (nx, ny) not in opp_terr else -1.0 * man(nx, ny, ox, oy)

        # Mild preference for increasing frontier expansion.
        if (nx, ny) in unclaimed:
            val += 0.5 * sum((inb(nx + ddx, ny + ddy) and ((nx + ddx, ny + ddy) in unclaimed or (nx + ddx, ny + ddy) in opp_terr)) for ddx, ddy in dirs)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]