def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    target = None
    if resources:
        best = None  # (adv, -selfd, selfd, rx, ry)
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in blocked:
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            cand = (adv, -sd, sd, rx, ry)
            if best is None or cand > best:
                best = cand
        if best is not None:
            _, _, _, tx, ty = best
            target = (tx, ty)

    if target is None:
        tx, ty = w // 2, h // 2
        target = (tx, ty)

    tx, ty = target
    prev_sd = cheb(sx, sy, tx, ty)
    prev_od = cheb(ox, oy, tx, ty)

    def nearest_obst_dist(x, y):
        if not obstacles:
            return 99
        best = 99
        for bx, by in obstacles:
            d = cheb(x, y, bx, by)
            if d < best:
                best = d
        return best

    best_move = None  # (score, -new_sd, new_od, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        new_sd = cheb(nx, ny, tx, ty)
        new_od = cheb(ox, oy, tx, ty)
        self_improve = prev_sd - new_sd
        opp_improve = new_od - prev_od  # negative if opponent closer next? (opponent position fixed here)
        obst = nearest_obst_dist(nx, ny)
        score = (self_improve * 10) + (-abs(new_sd) * 0.1) + (opp_improve * 0.5) + (obst * 0.05)
        cand = (score, -new_sd, new_od, dx, dy)
        if best_move is None or cand > best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [best_move[3], best_move[4]]