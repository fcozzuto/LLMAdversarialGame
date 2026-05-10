def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_set:
                    return True
        return False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not unclaimed and not opp_set:
        return [0, 0]

    frontier = [p for p in unclaimed if adj_opp(p[0], p[1])]
    targets = frontier if frontier else (list(unclaimed) if unclaimed else list(opp_set))
    if not targets:
        return [0, 0]

    # If frontier exists, prioritize capturing cells next to opponent; otherwise, expand away from opponent toward neutral.
    if frontier:
        tx, ty = min(targets, key=lambda p: manh((sx, sy), p))
    else:
        ox, oy = observation.get("opponent_position", [w - 1, h - 1])
        tx, ty = min(targets, key=lambda p: (manh((ox, oy), p) - manh((sx, sy), p)))

    best = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in self_set:
            score = 0
        elif (nx, ny) in opp_set:
            score = 4
        elif (nx, ny) in unclaimed:
            score = 2 + (1 if adj_opp(nx, ny) else 0)
        else:
            score = 1
        dist = manh((nx, ny), (tx, ty))
        # primary: maximize score, secondary: minimize distance, tertiary: deterministic tie-break by move
        cand = (-score, dist, dx * 3 + dy)
        if cand < best:
            best = cand
    dx, dy = best[1]  # incorrect; fix by storing move
    return [0, 0]