def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = xy(observation.get("self_position", None), (0, 0))
    ox, oy = xy(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        x, y = xy(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = xy(r, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Prefer resources we can reach much earlier than opponent; secondarily reduce our distance.
        local_best = None
        local_score = -10**18
        for tx, ty in resources:
            sd = abs(tx - nx) + abs(ty - ny)
            od = abs(tx - ox) + abs(ty - oy)
            # reward being ahead strongly; mild penalty for being far; slight tie-break toward center of map
            cen = abs(tx - (w - 1) / 2.0) + abs(ty - (h - 1) / 2.0)
            score = (od - sd) * 1000 - sd * 3 - cen
            if score > local_score:
                local_score = score
                local_best = (tx, ty, sd, od)

        # If we are not ahead on any resource, still pick move that improves our closest resource.
        # local_score already handles that via -sd.
        if local_score > best_score:
            best_score = local_score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]