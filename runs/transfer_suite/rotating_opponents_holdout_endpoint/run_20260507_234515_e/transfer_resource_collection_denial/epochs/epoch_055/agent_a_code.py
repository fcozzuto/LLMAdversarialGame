def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    valid_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                valid_resources.append((x, y))
    if not valid_resources:
        # Fallback: step that increases distance to opponent, preferring obstacle-safe.
        best = None
        for dx, dy, nx, ny in cand:
            key = (abs(nx - ox) + abs(ny - oy), -(abs(nx - sx) + abs(ny - sy)), dx, dy)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource that maximizes my advantage over opponent.
    best_target = None
    best_tkey = None
    for tx, ty in valid_resources:
        md = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        tkey = (od - md, -md, tx, ty)  # maximize advantage, then closer
        if best_tkey is None or tkey > best_tkey:
            best_tkey = tkey
            best_target = (tx, ty)

    tx, ty = best_target

    # From current step options, choose one that improves chance to be first on the target.
    best = None
    for dx, dy, nx, ny in cand:
        my_d = man(nx, ny, tx, ty)
        op_d = man(ox, oy, tx, ty)
        # Also prefer moving onto the target sooner, and avoid stepping too far from target.
        key = (op_d - my_d, -my_d, -(man(nx, ny, sx, sy)), dx, dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]