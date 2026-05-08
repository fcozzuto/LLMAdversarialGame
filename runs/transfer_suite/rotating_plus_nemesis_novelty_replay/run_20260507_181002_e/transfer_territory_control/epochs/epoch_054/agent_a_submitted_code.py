def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    unclaimed = toset(observation.get("unclaimed_cells"))

    if unclaimed:
        targets = unclaimed
    elif resources:
        targets = resources
    else:
        targets = set(selfT)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target(x, y):
        if targets:
            best = None
            bd = 10**9
            for tx, ty in targets:
                if (tx, ty) in obstacles:
                    continue
                d = abs(tx - x) + abs(ty - y)
                if d < bd:
                    bd = d
                    best = (tx, ty)
            return best
        return None

    tx, ty = best_target(sx, sy)
    if tx is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = - (abs(nx - tx) + abs(ny - ty))
        if (nx, ny) in resources:
            val += 20
        if (nx, ny) in unclaimed:
            val += 10
        if selfT and (nx, ny) in selfT:
            val += 3
        if oppT and (nx, ny) in oppT:
            val -= 30
        # keep away from opponent when near
        od = abs(nx - ox) + abs(ny - oy)
        val += min(10, od)
        # small deterministic tie-break
        val += (dx + 1) * 0.01 + (dy + 1) * 0.001
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0):
        # if everything was blocked, allow a safe fallback toward target
        # (still deterministic)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]