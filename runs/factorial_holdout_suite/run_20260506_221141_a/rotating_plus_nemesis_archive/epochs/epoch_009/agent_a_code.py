def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, cx, cy)
            key = (d, nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Pick target resource where we currently have the strongest advantage.
    best_res = None
    for p in resources:
        rx, ry = p[0], p[1]
        adv = man(ox, oy, rx, ry) - man(sx, sy, rx, ry)  # positive => we arrive sooner
        sd = man(sx, sy, rx, ry)
        key = (-adv, sd, rx, ry)
        if best_res is None or key < best_res[0]:
            best_res = (key, rx, ry)
    _, tx, ty = best_res

    # Move to maximize post-move advantage over the chosen target.
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        advantage_after = man(ox, oy, tx, ty) - man(nx, ny, tx, ty)
        d_after = man(nx, ny, tx, ty)
        key = (-advantage_after, d_after, nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [best_move[1], best_move[2]] if best_move else [0, 0]