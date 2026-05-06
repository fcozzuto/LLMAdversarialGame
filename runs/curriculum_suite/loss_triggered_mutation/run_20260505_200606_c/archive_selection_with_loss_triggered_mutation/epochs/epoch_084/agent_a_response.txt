def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = int(observation.get("self_position", [0, 0])[0]), int(observation.get("self_position", [0, 0])[1])
    ox, oy = int(observation.get("opponent_position", [w - 1, h - 1])[0]), int(observation.get("opponent_position", [w - 1, h - 1])[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Precompute resource stats from current positions for deterministic baseline tie-breaking
    res_list = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        drs = man(sx, sy, rx, ry)
        dro = man(ox, oy, rx, ry)
        res_list.append((rx, ry, drs, dro))
    res_list.sort(key=lambda t: (t[2], t[3], t[0], t[1]))

    best_dx, best_dy = 0, 0
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Score: prioritize resources where we gain over opponent (our advantage), then closeness, then avoid moving near opponent.
        best_adv = -10**9
        best_self = 10**9
        best_opp = 10**9
        target_x = 0
        target_y = 0

        for rx, ry, _, _ in res_list:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - our_d  # higher means we are closer than opponent
            if (adv > best_adv) or (adv == best_adv and (our_d < best_self or (our_d == best_self and (opp_d < best_opp)))):
                best_adv = adv
                best_self = our_d
                best_opp = opp_d
                target_x, target_y = rx, ry

        # Additional shaping: if we can land adjacent/at the closest resource now, it helps.
        # Also discourage moving into being too close to opponent (prevents accidental interception losses).
        opp_proximity = man(nx, ny, ox, oy)
        closest_current = man(sx, sy, target_x, target_y)
        reachable_bonus = 1 if best_self <= 1 else 0
        # Key uses negated terms for minimization
        key = (
            -reachable_bonus,
            -(best_adv),
            best_self,
            best_opp,
            abs(nx - target_x) + abs(ny - target_y),
            opp_proximity,
            dx,
            dy,
            nx,
            ny
        )
        if best_key is None or key < best_key:
            best_key = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]