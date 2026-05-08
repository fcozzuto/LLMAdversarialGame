def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(t) for t in (observation.get("unclaimed_cells") or [])]
    resources = [tuple(t) for t in (observation.get("resources") or [])]

    targets = []
    if resources:
        targets = resources
    elif unclaimed:
        targets = unclaimed
    else:
        targets = [(w // 2, h // 2)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if (nx, ny) in opp_terr:
            continue

        d_t = 10**9
        for tx, ty in targets:
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                dt = abs(tx - nx) + abs(ty - ny)
                if dt < d_t:
                    d_t = dt

        d_o = man((nx, ny), (ox, oy))
        in_self = 1 if (nx, ny) in self_terr else 0
        score = (-(d_t)) + 2 * d_o + in_self * 0.5
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]