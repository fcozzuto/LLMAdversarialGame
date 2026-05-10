def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_raw if p and len(p) >= 2}
    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if (sx, sy) in obstacles:
        obstacles.remove((sx, sy))
    if (sx, sy) in set(res):
        return [0, 0]
    if not res:
        return [0, 0]

    # Pick target resource that maximizes "arrival advantage" for us.
    best = None
    for tx, ty in res:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer ours earlier; break ties by closer and then by position (deterministic).
        key = (-(od - sd), sd, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty), sd, od)
    (tx, ty) = best[1]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = man(nx, ny, tx, ty)
        # Encourage immediate capture and blocking closeness.
        opp_near = man(ox, oy, tx, ty)
        on_res = 1 if (nx, ny) in set(res) else 0
        # Smaller is better.
        score = (ns - on_res * 10, on_res * -1, (opp_near - ns), abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move is None or score < best_move[0]:
            best_move = (score, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]