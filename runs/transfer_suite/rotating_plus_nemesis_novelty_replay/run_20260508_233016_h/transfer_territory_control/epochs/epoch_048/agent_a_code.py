def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    if not self_terr:
        self_terr = {(sx, sy)}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target = None
    if unclaimed:
        adj = []
        for ux, uy in unclaimed:
            ok = ((ux - 1, uy) in self_terr) or ((ux + 1, uy) in self_terr) or ((ux, uy - 1) in self_terr) or ((ux, uy + 1) in self_terr)
            if ok:
                adj.append((ux, uy))
        pool = adj if adj else unclaimed
        best = None
        bestd = 10**9
        for tx, ty in pool:
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            d = man(sx, sy, tx, ty)
            if d < bestd or (d == bestd and (best is None or (tx, ty) < best)):
                bestd, best = d, (tx, ty)
        target = best
    if target is None:
        tx, ty = w // 2, h // 2
        if not inb(tx, ty):
            tx, ty = min(max(tx, 0), w - 1), min(max(ty, 0), h - 1)
        if (tx, ty) in obstacles:
            tx, ty = sx, sy
        target = (tx, ty)

    best_move = (0, 0)
    best_score = -10**18
    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = -man(nx, ny, tx, ty)
        if dx == 0 and dy == 0:
            score -= 0.1
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)
    return [best_move[0], best_move[1]]