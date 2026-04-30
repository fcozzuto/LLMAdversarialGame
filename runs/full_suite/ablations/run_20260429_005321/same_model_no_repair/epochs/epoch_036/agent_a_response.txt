def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best_r = None
    best_val = -10**18
    cx0 = (gw - 1) / 2.0
    cy0 = (gh - 1) / 2.0
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        center_bias = -0.002 * (((rx - cx0) ** 2) + ((ry - cy0) ** 2))
        val = (do - ds) * 1000 - ds * 3 + center_bias
        if val > best_val or (val == best_val and (rx, ry) < (best_r[0], best_r[1]) if best_r else True):
            best_val = val
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    rx, ry = best_r

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]
    cur_do = man(ox, oy, sx, sy)

    best_move = (0, 0)
    best_move_score = -10**18
    for dx, dy in deltas:
        nsx, nsy = sx + dx, sy + dy
        if not inb(nsx, nsy) or (nsx, nsy) in obs:
            continue
        dsn = man(nsx, nsy, rx, ry)
        don = man(ox, oy, nsx, nsy)
        move_score = -dsn * 10 + (don - cur_do) * 1 + (1 if (nsx, nsy) == (rx, ry) else 0) * 50
        if move_score > best_move_score or (move_score == best_move_score and (dx, dy) < best_move):
            best_move_score = move_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]