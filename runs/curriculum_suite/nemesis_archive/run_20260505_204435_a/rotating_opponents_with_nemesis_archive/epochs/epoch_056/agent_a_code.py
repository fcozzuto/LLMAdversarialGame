def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not rpos:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    row_targets = [p for p in rpos if p[1] == oy]
    col_targets = [p for p in rpos if p[0] == ox]

    def pick(targets):
        best = None
        bestv = None
        for tx, ty in targets:
            v = md(sx, sy, tx, ty)
            if bestv is None or v < bestv:
                bestv = v
                best = (tx, ty)
        return best

    target = pick(row_targets) or pick(col_targets) or pick(rpos)

    tx, ty = target
    best_move = (0, 0)
    best_val = None
    opp_to_target = md(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            nx, ny = sx, sy
            dx, dy = 0, 0
        my_to_target = md(nx, ny, tx, ty)
        penalty = 0
        if ny == oy and my_to_target >= opp_to_target:
            penalty = 5
        val = my_to_target + penalty
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]