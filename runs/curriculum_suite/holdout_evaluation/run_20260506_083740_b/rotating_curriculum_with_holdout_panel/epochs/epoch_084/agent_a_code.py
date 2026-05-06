def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def passable(x, y):
        return inb(x, y) and (x, y) not in ob

    def man(a, b, c, d):
        a, b, c, d = abs(a - c), abs(b - d), 0, 0
        return a + b

    parsed_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                parsed_resources.append((x, y))
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
            if 0 <= x < w and 0 <= y < h:
                parsed_resources.append((x, y))

    tx, ty = None, None
    if parsed_resources:
        bestd, tx, ty = 10**9, parsed_resources[0][0], parsed_resources[0][1]
        for x, y in parsed_resources:
            d = abs(sx - x) + abs(sy - y)
            if d < bestd or (d == bestd and (x, y) < (tx, ty)):
                bestd, tx, ty = d, x, y
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        score = - (abs(nx - tx) + abs(ny - ty))
        score += -0.05 * (abs(nx - ox) + abs(ny - oy))
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)

    dx, dy = best_move
    if passable(sx + dx, sy + dy):
        return [dx, dy]

    # guaranteed fallback: pick first passable move deterministically
    for dx, dy in moves:
        if passable(sx + dx, sy + dy):
            return [dx, dy]
    return [0, 0]