def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if not resources:
        best = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dc = abs(nx - cx) + abs(ny - cy)
            do = man(nx, ny, ox, oy)
            score = dc + 0.12 * do
            if best is None or score < best:
                best = score
                best_move = [dx, dy]
        return best_move

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        do = man(nx, ny, ox, oy)
        # Slightly discourage getting "swept": if opponent is same row/column, keep a bit of lateral separation.
        row_col_sweep = (1.0 if ny == oy or nx == ox else 0.0)

        m = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do_r = man(ox, oy, rx, ry)
            adv = ds - 0.65 * do_r  # lower is better: win the resource race
            if nx == rx and ny == ry:
                adv -= 6.0
            if m is None or adv < m:
                m = adv

        stay_pen = 0.25 if dx == 0 and dy == 0 else 0.0
        opp_pen = 0.18 * max(0, 4 - do)  # avoid being too close when race is uncertain
        score = m + opp_pen + row_col_sweep * 0.35 + stay_pen

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move