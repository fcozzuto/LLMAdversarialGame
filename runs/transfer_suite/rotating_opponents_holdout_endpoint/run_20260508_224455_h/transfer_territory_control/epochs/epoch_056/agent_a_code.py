def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for c in obstacles:
        if c is not None and len(c) >= 2:
            obs.add((int(c[0]), int(c[1])))

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    own = set((int(x), int(y)) for x, y in self_t if x is not None and y is not None)
    opp = set((int(x), int(y)) for x, y in opp_t if x is not None and y is not None)
    uq = set((int(x), int(y)) for x, y in unclaimed if x is not None and y is not None)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    opp_front = set()
    for (x, y) in uq:
        for nx, ny in neighbors(x, y):
            if (nx, ny) in opp:
                opp_front.add((x, y))
                break

    own_front = set()
    for (x, y) in uq:
        for nx, ny in neighbors(x, y):
            if (nx, ny) in own:
                own_front.add((x, y))
                break

    front = opp_front if opp_front else (own_front if own_front else uq)

    def nearest_dist(p):
        if not front:
            return 999
        x, y = p
        best = 999
        for tx, ty in front:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        cell = (nx, ny)

        score = 0
        if cell in opp_front:
            score += 200
        if cell in own_front:
            score += 60
        if cell in uq:
            score += 15
        if cell in opp:
            score += 40  # stepping into opponent-owned flips on entry
        if cell in own:
            score += 5

        score -= 3 * nearest_dist(cell)

        # small tie-break to encourage progress away from being stuck
        if cell not in uq and cell not in opp:
            score -= 8

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]