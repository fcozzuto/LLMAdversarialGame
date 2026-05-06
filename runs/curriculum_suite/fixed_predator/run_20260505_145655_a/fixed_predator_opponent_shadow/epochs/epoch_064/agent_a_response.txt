def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def value_from_pos(px, py):
        if not resources:
            # Drift to center while not walking into obstacles
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return -((px - cx) ** 2 + (py - cy) ** 2)
        best = None
        for tx, ty in resources:
            d_me = man(px, py, tx, ty)
            d_opp = man(ox, oy, tx, ty)
            lead = d_opp - d_me
            # Slight tie-break toward nearer resources and away from being boxed by obstacles
            penalty = 0
            if (px, py) in obstacles:
                penalty += 100000
            v = lead * 1000 - d_me
            if best is None or v > best:
                best = v
        return best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = x, y  # engine will keep us here
        v = value_from_pos(nx, ny)
        if best_val is None or v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    # If we have no resources, ensure a deterministic purposeful move
    if not resources and best_move == (0, 0):
        # Prefer moving toward opponent only if it doesn't worsen center drift too much
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        mx, my = sign(tx - x), sign(ty - y)
        best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]