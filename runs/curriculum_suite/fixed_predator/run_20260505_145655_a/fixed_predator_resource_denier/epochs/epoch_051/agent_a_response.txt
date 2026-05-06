def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for rx, ry in resources:
        sd = mdist(sx, sy, rx, ry)
        od = mdist(ox, oy, rx, ry)
        score = (od - sd) * 7 - sd
        center_bias = -(((rx - (w - 1) / 2) ** 2) + ((ry - (h - 1) / 2) ** 2)) * 0.001
        t = (score + center_bias, -sd, rx, ry)
        if best is None or t > best:
            best = t
    _, _, tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = mdist(nx, ny, tx, ty)
        sd0 = mdist(sx, sy, tx, ty)
        # Prefer getting closer to target, and if possible, improve denial by widening distance gap vs opponent.
        my_after = d
        opp_after = mdist(ox, oy, tx, ty)
        denial = opp_after - my_after
        t = (denial, sd0 - d, -my_after, dx, dy, nx, ny)
        if bestm is None or t > bestm:
            bestm = t

    if bestm is None:
        return [0, 0]
    dx, dy = bestm[3], bestm[4]
    return [int(dx), int(dy)]