def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if abs(dx) > abs(dy):
            return abs(dx)
        return abs(dy)

    def step(nx, ny):
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    cx, cy = w // 2, h // 2

    def eval_cell(x, y):
        if not resources:
            return (cheb(x, y, ox, oy) - 0.05 * cheb(x, y, cx, cy))
        best_r = -10**18
        for rx, ry in resources:
            myd = cheb(x, y, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Prefer resources I can reach sooner than opponent; encourage faster picks.
            score = (oppd - myd) * 2.0 - 0.35 * myd
            if myd == 0:
                score += 50.0
            if score > best_r:
                best_r = score
        # Small tie-break: prefer reducing my closest distance overall.
        mind = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < mind:
                mind = d
        return best_r - 0.05 * mind

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = step(sx + dx, sy + dy)
        sc = eval_cell(nx, ny)
        # Deterministic tie-break: lexicographic on (dx, dy) after score.
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]