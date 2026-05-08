def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal or not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = 0

        for rx, ry in res:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            if ds == 0:
                score += 20000
            elif ds <= do:
                score += 2000 + (do - ds) * 50 - ds
            else:
                score += -ds * 2 - (ds - do) * 3

        # Small tie-break: drift toward any currently reachable resource
        # (keeps determinism without randomness)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]