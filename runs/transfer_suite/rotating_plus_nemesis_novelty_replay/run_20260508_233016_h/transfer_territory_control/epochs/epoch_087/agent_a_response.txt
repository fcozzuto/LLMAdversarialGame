def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(c) for c in (observation.get("unclaimed_cells") or [])]
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        return [(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    occ_opp = tuple((ox, oy) in oppT for _ in [0])  # harmless deterministic use

    opp_front = set()
    for (x, y) in oppT:
        for nx, ny in neigh8(x, y):
            if inb(nx, ny) and (nx, ny) not in oppT and (nx, ny) not in obstacles:
                opp_front.add((nx, ny))

    self_front = set()
    for (x, y) in selfT:
        for nx, ny in neigh8(x, y):
            if inb(nx, ny) and (nx, ny) not in selfT and (nx, ny) not in obstacles:
                self_front.add((nx, ny))

    target_pool = []
    for c in unclaimed:
        x, y = c
        score = 10**9
        if c in opp_front:
            score = man(x, y, sx, sy) * 2 + man(x, y, ox, oy)
        elif c in self_front:
            score = man(x, y, sx, sy) + man(x, y, ox, oy) + 50
        else:
            score = man(x, y, sx, sy) * 2 + man(x, y, ox, oy) + 200
        target_pool.append((score, x, y))
    if not target_pool:
        for x, y in opp_front:
            if (x, y) not in obstacles:
                target_pool.append((man(x, y, sx, sy) * 2 + man(x, y, ox, oy), x, y))
    if not target_pool:
        # fallback toward center-ish but prefer avoiding obstacles deterministically
        target_pool = [(man(w//2, h//2, sx, sy), w//2, h//2)]

    target_pool.sort()
    tx, ty = target_pool[0][1], target_pool[0][2]

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**18, 0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # prefer capturing: if stepping onto opp territory, prioritize heavily
        step_score = 0
        if (nx, ny) in oppT:
            step_score -= 100000
        # also prefer reducing distance to target and to opponent front
        step_score += man(nx, ny, tx, ty)
        if (nx, ny) in opp_front:
            step_score -= 5000
        # slight preference for expanding toward center
        step_score += (abs(nx - w/2) + abs(ny - h/2)) * 0.01
        # deterministic tie-break
        if (step_score, nx, ny) < best:
            best = (step_score, dx, dy)

    return [int(best[1]), int(best[2])]