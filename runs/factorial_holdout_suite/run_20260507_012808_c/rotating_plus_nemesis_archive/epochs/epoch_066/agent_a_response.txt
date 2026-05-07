def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        tx, ty = w - 1 - ox, h - 1 - oy
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    def dist(a, b, x, y):
        return abs(x - a) + abs(y - b)

    # Pick a target resource: prioritize being closer than opponent; then closest; then deterministic tie-break.
    best = None
    for (rx, ry) in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Higher is better
        score = (1 if ds <= do else 0) * 100000 - ds * 10 + do
        key = (-score, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # Choose move that minimizes distance to target; if tie, prefer moves that deny opponent (increase their distance) deterministically.
    best_move = (10**9, -10**9, 0, 0)
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d1 = abs(nx - tx) + abs(ny - ty)
        d2 = abs(ox - tx) + abs(oy - ty)
        # If we match/update target, opponent gets less chance: prefer larger opponent distance after our move.
        # Deterministic small preference: lexicographic on move.
        opp_bias = d2 - (0 if ds <= do else 0)
        cand = (d1, -opp_bias, ddx, ddy)
        if cand < best_move:
            best_move = cand

    if best_move[2] == 0 and best_move[3] == 0:
        return [0, 0]
    return [int(best_move[2]), int(best_move[3])]