def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    valids = [(r[0], r[1]) for r in resources if tuple(r) not in obstacles]
    if not valids:
        return [0, 0]

    best_r = None
    best_key = None
    for rx, ry in valids:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_to_target = man(ox, oy, tx, ty)

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd2 = man(nx, ny, tx, ty)
        # Primary: become closer to target than opponent effectively (distance gap).
        # Secondary: prefer shorter distance; tertiary: reduce opponent distance for contest control.
        gap = opp_to_target - sd2
        opp_d2 = man(nx, ny, ox, oy)
        score = (gap, -sd2, -opp_d2, - (dx == 0 and dy == 0))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]