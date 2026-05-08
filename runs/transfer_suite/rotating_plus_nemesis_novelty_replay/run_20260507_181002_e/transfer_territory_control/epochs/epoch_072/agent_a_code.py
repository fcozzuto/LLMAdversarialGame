def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = resources

    if not unclaimed:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    best_val = None

    # Greedy: step that minimizes distance to nearest target, tie-break away from opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        min_d = None
        for tx, ty in unclaimed:
            if min_d is None:
                min_d = abs(nx - tx) + abs(ny - ty)
            else:
                d = abs(nx - tx) + abs(ny - ty)
                if d < min_d:
                    min_d = d
        if min_d is None:
            continue
        opp_d = abs(nx - ox) + abs(ny - oy)
        val = (-min_d, opp_d)  # smaller min_d better; larger opp_d better
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]