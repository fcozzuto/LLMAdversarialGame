def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if opp_terr:
        ox = sum(x for x, _ in opp_terr) / float(len(opp_terr))
        oy = sum(y for _, y in opp_terr) / float(len(opp_terr))
    else:
        ox, oy = (w - 1) / 2.0, (h - 1) / 2.0

    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0:
            dx = -dx
        dy = y - b
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        if (nx, ny) == (sx, sy) and (dx, dy) != (0, 0):
            # obstacle bounce: engine keeps in place; still allow scoring
            pass

        if (nx, ny) in unclaimed:
            base = 3.0
        elif (nx, ny) in opp_terr:
            base = 6.0
        elif (nx, ny) in self_terr:
            base = 0.5
        else:
            base = 1.0  # should be unclaimed, but be safe

        # Prefer pushing away from opponent's current center, while capturing when possible.
        away = cheb(nx, ny, ox, oy)
        opp_near = 0
        for adx, ady in moves:
            if adx == 0 and ady == 0:
                continue
            ax2, ay2 = nx + adx, ny + ady
            if (ax2, ay2) in opp_terr:
                opp_near += 1

        # Encourage edge expansion: prefer moves that increase adjacency to unclaimed.
        adj_un = 0
        for adx, ady in moves:
            if adx == 0 and ady == 0:
                continue
            ax2, ay2 = nx + adx, ny + ady
            if (ax2, ay2) in unclaimed:
                adj_un += 1

        val = base + 0.35 * away + 0.8 * adj_un - 0.6 * opp_near

        # Deterministic tie-break: smallest dx, then dy
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]