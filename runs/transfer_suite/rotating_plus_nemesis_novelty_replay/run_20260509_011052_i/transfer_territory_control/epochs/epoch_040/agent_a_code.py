def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_terr = set()
    for p in observation.get("self_territory", []) or []:
        try:
            self_terr.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    opp_terr = set()
    for p in observation.get("opponent_territory", []) or []:
        try:
            opp_terr.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        try:
            unclaimed.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in opp_terr:
            sc += 100
        if (nx, ny) in unclaimed:
            sc += 40
        if (nx, ny) in self_terr:
            sc += 10
        # Prefer moving toward opponent to pressure/expand
        sc += -(abs(nx - ox) + abs(ny - oy))
        # Slight preference for continuing from own territory
        if (sx, sy) in self_terr:
            sc += 2
        # Prefer cells adjacent to our territory (frontier expansion)
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + ax, ny + ay
            if (tx, ty) in self_terr:
                sc += 6

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best