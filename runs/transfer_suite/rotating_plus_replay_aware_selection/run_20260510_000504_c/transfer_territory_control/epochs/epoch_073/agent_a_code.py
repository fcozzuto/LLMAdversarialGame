def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))

    resources = observation.get("resources") or []
    target = None
    if resources:
        tx, ty = resources[0][0], resources[0][1]
        target = (int(tx), int(ty))
    else:
        cand = []
        base = self_terr if self_terr else {tuple((sx, sy))}
        for x, y in base:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    cand.append((nx, ny))
        if cand:
            target = min(cand, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))

    if target is None:
        target = (int((w - 1) / 2), int((h - 1) / 2))

    def score_cell(x, y):
        if (x, y) in obstacles:
            return 10**9
        if x == ox and y == oy:
            return -10**6
        return abs(x - target[0]) + abs(y - target[1])

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_sc = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc < best_sc or (sc == best_sc and (best is None or (dx, dy) < best)):
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]