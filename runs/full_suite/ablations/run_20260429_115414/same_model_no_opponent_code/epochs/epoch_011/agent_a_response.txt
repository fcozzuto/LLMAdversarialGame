def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        resources = [[w - 1, h - 1]]

    # Pick resource that maximizes current advantage (opp farther than self), then prefer nearer
    best_r = None
    best_key = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -od, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    best_move = (0, 0)
    best_score = None
    cur_sd = cheb(sx, sy, tx, ty)
    cur_adv = cheb(ox, oy, tx, ty) - cur_sd

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        # Strongly prefer moves that keep/extend winning advantage; also avoid getting too close to opponent unless it helps
        close_op = cheb(nx, ny, ox, oy)
        bonus_target = 2 if sd < cur_sd else (0 if sd == cur_sd else -1)
        capture_rush = 20 if (nx, ny) == (tx, ty) else 0
        score = adv * 10 + bonus_target - sd - close_op + capture_rush + (cur_adv - adv) * 0.5
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not isinstance(dx, int) or not isinstance(dy, int):
        dx, dy = 0, 0
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [dx, dy]