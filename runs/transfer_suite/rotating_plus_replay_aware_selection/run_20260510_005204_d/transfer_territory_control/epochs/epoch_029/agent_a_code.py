def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    bestv = None
    cur_dist = abs(sx - ox) + abs(sy - oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        nd = abs(nx - ox) + abs(ny - oy)
        gain = 0
        risk = 0
        if (nx, ny) in unclaimed:
            gain += 2
        if (nx, ny) in self_terr:
            gain += 0.3
        if (nx, ny) in opp_terr:
            risk += 3  # entering opponent territory likely helps them (even if flipping is enabled)
        # Prefer pushing away from opponent and toward frontier (adjacent unclaimed)
        frontier = 0
        for adx, ady in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)):
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) in unclaimed:
                frontier += 1
        if frontier:
            gain += 0.2 * frontier

        away = (nd - cur_dist)
        value = gain + 0.15 * nd + 0.4 * away - risk
        if best is None or value > bestv or (value == bestv and (dx, dy) < best):
            bestv = value
            best = (dx, dy)

    return [int(best[0]), int(best[1])]