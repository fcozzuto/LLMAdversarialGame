def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_move_toward(target):
        tx, ty = target
        moves = [(-1, -1), (0, -1), (1, -1),
                 (-1, 0), (0, 0), (1, 0),
                 (-1, 1), (0, 1), (1, 1)]
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            key = (d, abs((nx - ox)) + abs((ny - oy)), nx, ny, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        return best_move_toward((tx, ty))

    me = (sx, sy)
    opp = (ox, oy)

    # Prefer resources where we have a distance advantage; otherwise chase nearest.
    chosen = None
    for r in resources:
        d_me = man(me, r)
        d_opp = man(opp, r)
        # Higher advantage first; then fewer total steps; then deterministic tie.
        adv = d_opp - d_me
        key = (-adv, d_me + d_opp, r[0], r[1])
        if chosen is None or key < chosen[0]:
            chosen = (key, r)

    return best_move_toward(chosen[1])