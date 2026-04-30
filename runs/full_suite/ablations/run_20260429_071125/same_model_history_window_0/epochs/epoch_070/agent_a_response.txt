def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist_cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick resource I can reach sooner than opponent; otherwise closest to me.
    best = None
    best_score = None
    for rx, ry in resources:
        md = dist_cheb(sx, sy, rx, ry)
        od = dist_cheb(ox, oy, rx, ry)
        score = (od - md, -md)  # higher = I am closer; tie-break closer to me
        if best is None or score > best_score:
            best = (rx, ry)
            best_score = score

    tx, ty = best

    # Deterministic move selection: try moves that reduce chebyshev distance to target,
    # while avoiding obstacles and staying in bounds. Tie-break by fixed direction order.
    dirs = [
        (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    curd = dist_cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_newd = curd + 1
    for dx, dy in dirs:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist_cheb(nx, ny, tx, ty)
        if nd < best_newd:
            best_newd = nd
            best_move = (dx, dy)
    # If all reducing moves are blocked, pick the first valid non-obstacle move in fixed order.
    if best_move == (0, 0) and best_newd == curd + 1:
        for dx, dy in dirs:
            nx = sx + dx
            ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
    return [best_move[0], best_move[1]]