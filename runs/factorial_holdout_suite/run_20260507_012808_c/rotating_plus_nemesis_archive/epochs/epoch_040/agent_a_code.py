def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dxdy = [0, 0]
    best_key = None

    # Choose move that maximizes our advantage at next step.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # If staying invalid due to engine, it will keep us; but we only consider ok cells.
        best_adv = -10**9
        best_d = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not ok(rx, ry):
                continue
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds  # positive means we're closer than opponent
            if adv > best_adv or (adv == best_adv and ds < best_d):
                best_adv = adv
                best_d = ds
        # Secondary preference: move toward the most "contested" resource (small do).
        # Deterministic tie-breaker via coordinates.
        contested = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not ok(rx, ry):
                continue
            contested = min(contested, dist(ox, oy, rx, ry))
        key = (best_adv, -best_d, -contested, nx, ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_dxdy = [dx, dy]

    return best_dxdy