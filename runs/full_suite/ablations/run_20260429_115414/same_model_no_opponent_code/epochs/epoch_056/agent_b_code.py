def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose best move by maximizing (opponent distance advantage) minus our distance to nearest resource.
    best_move = (0, 0)
    best_score = -10**9

    targets = resources[:]
    if not targets:
        targets = [(w // 2, h // 2)]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = 10**9
        op_d = 10**9
        for tx, ty in targets:
            my_d = min(my_d, md(nx, ny, tx, ty))
            op_d = min(op_d, md(ox, oy, tx, ty))
        # Prefer closer to resources, and if we can be closer than opponent.
        score = (op_d - my_d) * 10 - my_d
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]