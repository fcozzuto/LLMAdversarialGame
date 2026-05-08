def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", (sx, sy))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_cells = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_cells = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh4(x, y):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    frontier = []
    if unclaimed:
        for ux, uy in unclaimed:
            for nx, ny in neigh4(ux, uy):
                if (nx, ny) in opp_cells:
                    frontier.append((ux, uy))
                    break

    target = None
    bestd = None
    target_list = frontier if frontier else (unclaimed if unclaimed else [(ox, oy)])
    for tx, ty in target_list:
        d = md(tx, ty, ox, oy)
        if bestd is None or d < bestd or (d == bestd and (tx, ty) < target):
            bestd = d
            target = (tx, ty)

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    bestscore = None
    tx, ty = target if target else (ox, oy)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = md(nx, ny, tx, ty)
        score = -dist
        if (nx, ny) in opp_cells:
            score += 50
        if (nx, ny) in self_cells:
            score += 5
        if bestscore is None or score > bestscore or (score == bestscore and (dx, dy) < best):
            bestscore = score
            best = (dx, dy)

    dx, dy = best if best is not None else (0, 0)
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]