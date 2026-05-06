def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list if p is not None and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources or w <= 0 or h <= 0:
        return [0, 0]

    best_r = resources[0]
    best_gap = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        gap = myd - opd  # larger => I'm farther, opponent likely to grab it first
        if gap > best_gap:
            best_gap = gap
            best_r = (rx, ry)
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        od = man(nx, ny, ox, oy)
        score = -d + 0.15 * od
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]