def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    resources = observation.get("resources") or []
    res_set = set((p[0], p[1]) for p in resources if p is not None and len(p) >= 2)
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neighbors = [(sx + dx, sy + dy, dx, dy) for dx, dy in moves if valid(sx + dx, sy + dy)]
    if not neighbors:
        return [0, 0]

    if res_set:
        best = None
        for nx, ny, dx, dy in neighbors:
            if (nx, ny) in res_set:
                return [dx, dy]
        targets = list(res_set)
        for nx, ny, dx, dy in neighbors:
            d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in targets)
            adv = (abs(ox - rx) + abs(oy - ry)) if targets else 0
            score = (-d, -(adv))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # No resources visible: hold unless opponent is adjacent, then step away deterministically.
    def man(x, y):
        return abs(x - ox) + abs(y - oy)

    best = None
    for nx, ny, dx, dy in neighbors:
        score = (man(nx, ny), -abs(dx) - abs(dy))
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]