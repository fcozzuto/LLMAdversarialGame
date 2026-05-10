def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose best resource target: maximize relative advantage (opponent distance - our distance).
    best = None  # (lead, -our_d, opp_d, rx, ry)
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd
        cand = (lead, -sd, od, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    tx, ty = best[3], best[4]
    cur_sd = cheb(sx, sy, tx, ty)
    cur_od = cheb(ox, oy, tx, ty)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    best_move = None  # (score, new_sd, lead, dx, dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        new_sd = cheb(nx, ny, tx, ty)
        new_od = cheb(ox, oy, tx, ty)
        lead = new_od - new_sd
        progress = cur_sd - new_sd
        # Prefer moves that increase/maintain relative lead, then reduce our distance.
        score = lead * 1000 + progress * 10 - new_sd
        cand = (score, new_sd, lead, dx, dy)
        if best_move is None or cand > best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [int(best_move[3]), int(best_move[4])]