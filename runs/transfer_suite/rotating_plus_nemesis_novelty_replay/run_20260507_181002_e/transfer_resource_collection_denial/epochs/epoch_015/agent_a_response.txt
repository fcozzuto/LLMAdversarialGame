def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", r.get("pos", None))
            if isinstance(q, (list, tuple)) and len(q) == 2:
                resources.append((int(q[0]), int(q[1])))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best_target = None
        best_val = -10**9
        for tx, ty in resources:
            our_d = man(sx, sy, tx, ty)
            opp_d = man(ox, oy, tx, ty)
            val = (opp_d - our_d) * 10 - our_d
            if val > best_val:
                best_val = val
                best_target = (tx, ty)
    else:
        best_target = None

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    best_move = (0, 0, -10**9)
    for dx, dy, nx, ny in legal:
        our_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        old_our_d = man(sx, sy, tx, ty)
        delta_our = old_our_d - our_d

        taken = 1 if (nx, ny) == (tx, ty) else 0
        # Add secondary pressure: discourage stepping into being closer to the same target than opponent
        opp_pressure = man(ox, oy, nx, ny) - man(ox, oy, sx, sy)

        score = 3 * taken + 5 * delta_our + (opp_d - our_d) + 0.2 * opp_pressure
        # Small deterministic bias to reduce dithering
        score += 0.001 * (dx * 3 + dy)

        if score > best_move[2]:
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]