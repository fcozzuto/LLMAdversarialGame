def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick target resource (or center if none)
    if resources:
        best = None
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer resources where we are closer; then closer to us; then farther from opponent
            score = (od <= sd, od - sd, -sd, -dist(ox, oy, w - 1 - rx, h - 1 - ry))
            if best is None:
                best = (score, rx, ry)
            else:
                if score[0] and not best[0][0]:
                    best = (score, rx, ry)
                elif score[0] == best[0][0] and (score[1], score[2], score[3]) > (best[0][1], best[0][2], best[0][3]):
                    best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_step = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = dist(nx, ny, tx, ty)
        opd = dist(nx, ny, ox, oy)
        # Maximize: stay safe and get closer to target while pushing away opponent
        key = (-myd, opd, -abs((w - 1 - nx)) - abs((h - 1 - ny)))
        if best_key is None or key > best_key:
            best_key = key
            best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]