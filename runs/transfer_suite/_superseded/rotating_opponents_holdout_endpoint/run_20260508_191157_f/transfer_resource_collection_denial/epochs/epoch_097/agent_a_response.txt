def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(a, b, x, y):
        return abs(a - x) + abs(b - y)

    rem = observation.get("remaining_resource_count", len(resources))
    scarcity = 1 if rem <= 4 else 0

    best_resource_overall = None
    best_overall_d = 10**9
    for rx, ry in resources:
        d = man(sx, sy, rx, ry)
        if d < best_overall_d:
            best_overall_d = d
            best_resource_overall = (rx, ry)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy))

    def eval_pos(nx, ny):
        win_cnt = 0
        win_weight = 0.0
        deny_weight = 0.0
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds < do:
                win_cnt += 1
                win_weight += (1.0 / (1 + ds)) + (0.7 if scarcity else 0.0)
            elif ds == do:
                win_weight += 0.25 / (1 + ds)
            else:
                deny_weight += (0.9 / (1 + do)) * (do - ds + 1)
        # If we can't secure many wins, switch to best "advantage" denials.
        adv_best = -10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = (do - ds)
            if adv > adv_best:
                adv_best = adv
        denom = 1 + (len(resources) - win_cnt)
        return (win_cnt, win_weight + (0.35 * deny_weight / denom), adv_best)

    best = None
    best_key = None
    best_secondary = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        key = eval_pos(nx, ny)
        # Secondary: get closer to the closest resource overall; then deterministic tie by move order.
        sec = man(nx, ny, best_resource_overall[0], best_resource_overall[1]) if best_resource_overall else 0
        if best_key is None or key > best_key or (key == best_key and sec < best_secondary) or (key == best_key and sec == best_secondary and (dx, dy) < best):
            best = (dx, dy)
            best_key = key
            best_secondary = sec
    return [best[0], best[1]]