def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs = set(map(tuple, observation.get("obstacles", [])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Interceptor target: predict where opponent 2 steps from their current direction to a chosen resource.
    best_resource = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources opponent is close to (we need to intercept), but choose ones where we can also plausibly reach.
        key = (1 if od <= sd else 0, 2 * od - sd, -od, rx, ry)
        if best_key is None or key > best_key:
            best_key, best_resource = key, (rx, ry)

    rx, ry = best_resource
    dx_o = 0 if ox == rx else (1 if rx > ox else -1)
    dy_o = 0 if oy == ry else (1 if ry > oy else -1)
    ix, iy = ox + 2 * dx_o, oy + 2 * dy_o
    # Clamp and keep deterministic obstacle-aware fallback to a nearby free cell.
    ix = 0 if ix < 0 else (w - 1 if ix >= w else ix)
    iy = 0 if iy < 0 else (h - 1 if iy >= h else iy)

    if (ix, iy) in obs:
        # Try small deterministic offsets around intercept.
        candidates = []
        for a in [0, -1, 1, -2, 2]:
            for b in [0, -1, 1, -2, 2]:
                nx, ny = ix + a, iy + b
                if valid(nx, ny):
                    candidates.append((man(sx, sy, nx, ny), nx, ny))
        if candidates:
            _, ix, iy = min(candidates)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Move to intercept; secondary objective: avoid letting opponent get closer to the resource than we do.
        self_to_int = man(nx, ny, ix, iy)
        self_to_res = man(nx, ny, rx, ry)
        opp_to_res = man(ox, oy, rx, ry)
        opp_adv = opp_to_res - self_to_res  # larger => we are closer
        score = (opp_adv, -self_to_int, -man(nx, ny, ox, oy), -nx, -ny)
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]