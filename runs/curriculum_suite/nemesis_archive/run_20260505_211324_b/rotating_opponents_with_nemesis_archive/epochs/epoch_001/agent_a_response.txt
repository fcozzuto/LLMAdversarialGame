def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            v = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Precompute opponent distance to each resource (squared)
    res_list = [tuple(r) for r in resources]
    oppd = []
    for rx, ry in res_list:
        dx = rx - ox
        dy = ry - oy
        oppd.append(dx * dx + dy * dy)

    cx, cy = w / 2.0, h / 2.0
    best_move = (0, 0)
    best_val = None

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose the resource where we gain most relative distance advantage
        max_margin = None
        min_self_dist_for_margin = None
        for i, (rx, ry) in enumerate(res_list):
            sxr = rx - nx
            syr = ry - ny
            self_dist = sxr * sxr + syr * syr
            margin = oppd[i] - self_dist
            if max_margin is None or margin > max_margin or (margin == max_margin and self_dist < min_self_dist_for_margin):
                max_margin = margin
                min_self_dist_for_margin = self_dist

        # Encourage moving toward center to break ties deterministically
        center_dist = (cx - nx) * (cx - nx) + (cy - ny) * (cy - ny)
        val = (max_margin, -min_self_dist_for_margin, -center_dist)

        if best_val is None or val > best_val or (val == best_val and (dxm, dym) < best_move):
            best_val = val
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]] if best_val is not None else [0, 0]