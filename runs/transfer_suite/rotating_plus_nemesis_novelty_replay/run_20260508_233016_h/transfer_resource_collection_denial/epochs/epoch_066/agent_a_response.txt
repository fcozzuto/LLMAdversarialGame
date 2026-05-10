def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    my_best = None
    my_best_key = None
    for rx, ry in resources:
        d1 = dist(sx, sy, rx, ry)
        d2 = dist(ox, oy, rx, ry)
        # Aim to secure first (d1<d2). If none, deny by maximizing opponent delay vs us.
        secure_score = (d2 - d1)  # positive means we are ahead
        tie_break = (-1 if (d1 < d2) else 1)
        key = (tie_break, -secure_score, d1, rx, ry)
        if my_best_key is None or key < my_best_key:
            my_best_key = key
            my_best = (rx, ry)

    tx, ty = my_best
    best_move = [0, 0]
    best_key = None

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = dist(nx, ny, tx, ty)
        op_d = dist(ox, oy, tx, ty)
        lead = op_d - my_d  # larger is better (we get closer sooner)
        # Secondary: keep away from direct resource points that opponent could steal next.
        # We approximate by penalizing moves that increase distance to the best resource.
        sec_pen = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            if dist(nx, ny, rx, ry) <= dist(sx, sy, rx, ry):
                sec_pen += 1 if dist(ox, oy, rx, ry) <= dist(nx, ny, rx, ry) else 0
        key = (-lead, my_d, sec_pen, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move