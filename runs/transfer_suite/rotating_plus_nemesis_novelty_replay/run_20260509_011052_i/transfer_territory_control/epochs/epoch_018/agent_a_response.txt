def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def adj_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in S:
                c += 1
        return c

    candidates = []
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0.0

        if (nx, ny) in opp_terr:
            score += 30.0 + 5.0 * adj_count(nx, ny, opp_terr)

        if (nx, ny) in self_terr:
            score += 2.0  # reinforce (territory is valuable)
        if (nx, ny) in unclaimed:
            score += 6.0 + 2.0 * adj_count(nx, ny, unclaimed)

        # Frontier bias: move toward border of our territory (prefer spreading)
        if (nx, ny) not in self_terr:
            score += 1.5

        # Center control
        score += -0.45 * (abs(nx - cx) + abs(ny - cy))

        # Try to occupy cells that are adjacent to opponent territory to counterclaim
        score += 3.5 * adj_count(nx, ny, opp_terr)

        # Prefer steps that increase "reachable" open cells (lightweight)
        open_n = 0
        for ddx, ddy in dirs8:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) not in obstacles and ((tx, ty) in opp_terr or (tx, ty) in unclaimed or (tx, ty) in self_terr):
                open_n += 1
        score += 0.15 * open_n

        candidates.append((score, -abs(dx) - abs(dy), dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    # Deterministic tie-break: higher score, then fewer diagonal/axis moves, then lexicographic dx,dy
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    return [int(candidates[0][2]), int(candidates[0][3])]