def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def is_obs(x, y): return (x, y) in obstacles

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    cx, cy = w // 2, h // 2

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or is_obs(nx, ny):
            continue

        score = 0.0
        if (nx, ny) in self_t:
            score += 1.0
        elif (nx, ny) in unclaimed:
            score += 3.0
        elif (nx, ny) in opp_t:
            score += 5.5
        else:
            score += 0.2

        score += 0.2 * (-(abs(nx - cx) + abs(ny - cy))) / 16.0
        score += 0.05 * (-(abs(nx - ox) + abs(ny - oy))) / 16.0

        neigh_unclaimed = 0
        neigh_opp = 0
        for ddx, ddy in neigh8:
            xx, yy = nx + ddx, ny + ddy
            if inb(xx, yy) and not is_obs(xx, yy):
                if (xx, yy) in unclaimed:
                    neigh_unclaimed += 1
                elif (xx, yy) in opp_t:
                    neigh_opp += 1
        score += 0.8 * neigh_unclaimed
        score += 0.5 * neigh_opp

        if score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]