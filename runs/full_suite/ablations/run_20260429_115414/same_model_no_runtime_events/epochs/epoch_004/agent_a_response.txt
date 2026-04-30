def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
    else:
        def cheb(a, b):
            dx = a[0] - b[0]; dx = dx if dx >= 0 else -dx
            dy = a[1] - b[1]; dy = dy if dy >= 0 else -dy
            return dx if dx > dy else dy

        sd0 = (sx, sy); od0 = (ox, oy)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            s_time = cheb(sd0, (rx, ry))
            o_time = cheb(od0, (rx, ry))
            # Prefer resources we can reach earlier; otherwise reduce their advantage.
            time_adv = o_time - s_time  # higher is better for us
            # Tie-break deterministically to avoid dithering.
            key = (time_adv, -s_time, -((rx * 37 + ry * 53) % 10000019), rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        if best is None:
            cx, cy = w // 2, h // 2
            tx, ty = cx, cy
        else:
            tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb_xy(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Move evaluation: we want to get closer to target and (secondarily) farther from it for opponent.
        my = cheb_xy(nx, ny, tx, ty)
        opp = cheb_xy(ox, oy, tx, ty)
        # also discourage stepping "around" by preferring smaller my, then smaller (my-opp)
        key = (-my, (my - opp), -((nx * 29 + ny * 31) % 1000003), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]