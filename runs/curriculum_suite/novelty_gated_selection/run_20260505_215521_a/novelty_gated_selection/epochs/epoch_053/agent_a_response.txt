def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst_list = observation.get("obstacles", []) or []
    obst = set()
    for p in obst_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources_list = observation.get("resources", []) or []
    resources = []
    for r in resources_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if w <= 0 or h <= 0:
        return [0, 0]

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        if resources:
            dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            dres = 0

        dop = abs(nx - ox) + abs(ny - oy)

        near_ob = 0
        for ex in (nx - 1, nx, nx + 1):
            for ey in (ny - 1, ny, ny + 1):
                if (ex, ey) in obst:
                    near_ob += 1

        center = -(abs(nx - cx) + abs(ny - cy))
        score = (-1.0 * dres) + (0.45 * dop) + (0.03 * center) - (1.25 * near_ob)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move