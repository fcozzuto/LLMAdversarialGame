def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    res_list = observation.get("resources") or []
    resources = []
    for p in res_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_op = abs(nx - ox) + abs(ny - oy)
        corner_best = 0
        for cx, cy in corners:
            corner_best = max(corner_best, abs(nx - cx) + abs(ny - cy))

        d_res = None
        if resources:
            d_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)

        if evader:
            score = (10_000 * d_op) + (1000 * corner_best) + (-(d_res if d_res is not None else 0))
        else:
            score = (10_000 * (-d_op)) + (2000 * (-(d_res if d_res is not None else 0))) + (0)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) > best):
            best_score = score
            best = (dx, dy)

    if best is None:
        if ok(sx, sy):
            return [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [int(best[0]), int(best[1])]