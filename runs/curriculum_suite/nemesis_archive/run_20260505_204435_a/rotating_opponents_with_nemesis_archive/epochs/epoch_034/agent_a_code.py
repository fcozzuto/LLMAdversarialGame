def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no resources known, retreat/hold space away from opponent.
    if not targets:
        best, bestv = (0, 0), -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best, bestv = (0, 0), -10**18
    opp_adj = (abs(sx - ox) <= 1 and abs(sy - oy) <= 1)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        self_best = 10**9
        opp_best = 10**9
        for tx, ty in targets:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            if sd < self_best:
                self_best = sd
            if od < opp_best:
                opp_best = od
        # Core: get closer to resources while being harder to contest.
        # Also: prefer increasing own distance from opponent when very close.
        v = (-self_best)
        # Deny: if opponent is already very close to some resource, push away to avoid easy steals.
        v += 0.6 * (man(nx, ny, ox, oy))
        # If opponent would be closer to resources than we are, add more weight to escaping.
        if opp_best < self_best:
            v += 2.0 * (man(nx, ny, ox, oy))
        # When adjacent, prioritize moving to cells that maximize immediate separation.
        if opp_adj:
            v += 3.0 * (man(nx, ny, ox, oy))
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]