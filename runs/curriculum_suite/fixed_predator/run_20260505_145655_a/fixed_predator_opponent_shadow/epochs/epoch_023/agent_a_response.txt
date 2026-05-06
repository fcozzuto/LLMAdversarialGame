def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Primary: maximize lead (we closer than opponent). Secondary: minimize our distance.
        key = (d_opp - d_me, -d_opp, -d_me)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx0 = sign(tx - x)
    dy0 = sign(ty - y)

    # Try best direct step(s) toward target; otherwise pick best safe alternative.
    candidates = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        # Score: prefer moving closer to target, avoid giving opponent access by also moving away from them.
        newd = abs(tx - nx) + abs(ty - ny)
        oppd = abs(tx - ox) + abs(ty - oy)
        # If dx,dy matches the coarse direction, add a small bonus for determinism/commitment.
        align = (dx == dx0 and dy == dy0) or (dx == dx0 and dy0 == 0 and dy == 0) or (dy == dy0 and dx0 == 0 and dx == 0)
        candidates.append((newd, -oppd, 0 if not align else -0.01, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    return [int(candidates[0][3]), int(candidates[0][4])]