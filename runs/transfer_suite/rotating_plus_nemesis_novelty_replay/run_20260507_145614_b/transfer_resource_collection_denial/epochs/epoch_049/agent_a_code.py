def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, x, y):
        return abs(x - a) + abs(y - b)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    for r in resources:
        if sx == r[0] and sy == r[1]:
            return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = (0, 0)
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        self_center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        # Choose best resource to pursue after this move
        best_target = -10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Intercept pressure: prefer resources we are not behind on; otherwise reduce opponent advantage.
            ahead_bonus = 0
            if sd <= od:
                ahead_bonus = 20 - sd
            else:
                ahead_bonus = -(od - sd) - sd * 0.1
            # Slight preference for nearer targets and for cells that keep us progressing.
            prog = -(sd) + 0.05 * (dist(nx, ny, sx, sy))
            tie = -0.001 * (abs(od - sd) + abs(rx - ox) + abs(ry - oy))
            val = ahead_bonus + prog + tie
            if val > best_target:
                best_target = val

        # If we can step onto a resource, do it decisively.
        on_resource = 0
        for rx, ry in resources:
            if nx == rx and ny == ry:
                on_resource = 1_000_000
                break

        total = on_resource + best_target + 0.02 * self_center
        if total > best_val:
            best_val = total
            best = (dxm, dym)

    return [best[0], best[1]]