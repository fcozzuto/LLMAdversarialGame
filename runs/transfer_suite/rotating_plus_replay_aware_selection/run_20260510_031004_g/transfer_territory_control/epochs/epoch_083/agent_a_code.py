def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    un = [tuple(c) for c in unclaimed if inb(c[0], c[1]) and not blocked(c[0], c[1])]
    if not un:
        # If no unclaimed, push toward opponent territory edges to counterclaim
        un = [p for p in opp_terr if inb(p[0], p[1]) and not blocked(p[0], p[1])]

    # Pick top few targets deterministically by combined proximity-to-self and "pressure" toward opponent
    targets = []
    for tx, ty in un:
        ds = abs(tx - sx) + abs(ty - sy)
        do = abs(tx - ox) + abs(ty - oy)
        # pressure: prefer cells closer to opponent than us (steal/counter)
        pressure = do - ds
        targets.append((ds * 3 + (0 if (tx, ty) in opp_terr else -press_think(pressure)) , ds, pressure, tx, ty))
    targets.sort()
    candidates = [(t[3], t[4]) for t in targets[:8]]

    best = None
    bestscore = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        # Evaluate landing cell
        minds = 10**9
        mindo = 10**9
        for tx, ty in candidates:
            d = abs(tx - nx) + abs(ty - ny)
            if d < minds: minds = d
            d2 = abs(tx - ox) + abs(ty - oy)
            if d2 < mindo: mindo = d2
        # Encourage moving toward frontier: unclaimed first, then opponent cells; avoid moving deeper into opponent distance
        in_self = (nx, ny) in self_terr
        in_opp = (nx, ny) in opp_terr
        in_un = (nx, ny) in set(unclaimed) if unclaimed else False
        score = 0
        if in_un: score += 80
        if in_opp: score += 60
        if in_self: score += 10
        # Prefer decreasing distance to chosen targets, and slightly prefer increasing opponent distance from landing
        score += (20 - minds)
        score += (-abs(nx - ox) - abs(ny - oy)) * 0.5
        # Penalize staying still unless clearly best by target
        if dx == 0 and dy == 0:
            score -= 8
        if best is None or score > bestscore:
            bestscore = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]

def press_think(p):
    # deterministic monotone helper without extra imports
    if p >= 0: return 0
    if p <= -6: return 6
    return -p