def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx = w // 2
        ty = 0 if oy > sy else h - 1
        best = (10**9, 10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, tx, ty)
            cand = (d, abs(dx) + abs(dy), nx, ny, dx, dy)
            if cand < best:
                best = cand
        return [best[4], best[5]] if best[0] != 10**9 else [0, 0]

    best_r = None
    best_key = None
    for p in resources:
        rx, ry = p[0], p[1]
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        # Prefer winning resource; then closer; then deterministic by position
        key = (-adv, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_move = (10**9, 10**9, 0, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # Small tie-break: avoid stepping away from target and slightly avoid opponent proximity
        opp_d = man(nx, ny, ox, oy)
        cand = (d, -opp_d, abs(dx) + abs(dy), nx, ny, dx, dy)
        if best_move[0] == 10**9 or cand < best_move:
            best_move = cand
    if best_move[0] == 10**9:
        return [0, 0]
    return [best_move[5], best_move[6]]