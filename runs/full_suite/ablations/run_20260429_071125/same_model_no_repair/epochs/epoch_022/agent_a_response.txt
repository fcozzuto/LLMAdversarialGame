def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    # Pick contested target: minimize (our_dist - 0.6*opp_dist)
    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in occ:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        key = sd - 0.6 * od
        if best_key is None or key < best_key or (key == best_key and (rx < best_r[0] or (rx == best_r[0] and ry < best_r[1]))):
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    def obstacle_pen(x, y):
        if (x, y) in occ:
            return 10**9
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in occ:
                    pen += 4 if (ax == 0 or ay == 0) else 3
        return pen

    best_move = (0, 0)
    best_score = -10**18
    start_selfd = md(sx, sy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        selfd = md(nx, ny, tx, ty)
        oppd = md(ox, oy, tx, ty)  # keep opponent static for this move decision

        on_res = 1 if (nx, ny) == (tx, ty) else 0
        dist_gain = start_selfd - selfd  # positive is good

        score = 0
        score += 1200 * on_res
        score += 18 * dist_gain
        score += 0.25 * (oppd - selfd)  # we want to be the closer one
        score -= 2.2 * obstacle_pen(nx, ny)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tiebreak: prefer closer in Euclidean-ish then smaller dx,dy lexicographically
            if (selfd < md(sx + best_move[0], sy + best_move[1], tx, ty)) or (selfd == md(sx + best_move[0], sy + best_move[1], tx, ty) and (dx, dy) < best_move):
                best_move =