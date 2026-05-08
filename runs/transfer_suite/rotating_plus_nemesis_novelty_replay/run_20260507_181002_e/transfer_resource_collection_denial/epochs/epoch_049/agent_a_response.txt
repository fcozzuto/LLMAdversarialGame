def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return (int(p[0]), int(p[1]))
        return default

    sx, sy = pos(observation.get("self_position", None), (0, 0))
    ox, oy = pos(observation.get("opponent_position", None), (sx, sy))

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        p = pos(o, None)
        x, y = p[0], p[1]
        if p is not None and 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        p = pos(r, None)
        x, y = p[0], p[1]
        if p is not None and free(x, y):
            resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Deterministically drift toward board center if no targets.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            val = (abs(nx - cx) + abs(ny - cy), nx, ny)
            if best is None or val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    # Choose a resource that maximizes advantage over opponent (prefer earlier capture).
    best_target = None
    for tx, ty in resources:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        # prioritize large (od - sd); then smaller sd; then deterministic position
        key = (od - sd, -sd, -tx, -ty)
        if best_target is None or key > best_target[0]:
            best_target = (key, tx, ty)
    _, tx, ty = best_target

    # Pick move that greedily improves our distance, while keeping opponent farther (deterministic tie-break).
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        sd2 = abs(tx - nx) + abs(ty - ny)
        od2 = abs(tx - ox) + abs(ty - oy)  # opponent assumed static this turn
        val = (sd2, -od2, nx, ny)
        if best is None or val < best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]] if best is not None else [0, 0]