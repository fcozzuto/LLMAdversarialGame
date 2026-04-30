def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a target via "race" advantage (opponent closer -> negative, we want positive),
    # plus mild tie-breaks for safety/positioning.
    best_res = resources[0]
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # positive when we are closer to that resource
        # prefer targets we can reach no later than opponent; otherwise still allow but penalize
        reach_term = 0 if sd <= od else -2 * (sd - od)
        # mild center bias to avoid drifting
        center_bias = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        key = (adv + reach_term, -sd, center_bias, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res

    # Next move: greedily reduce our distance to target, but avoid allowing opponent to get closer
    # to the same target by more than we improve.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = man(nx, ny, rx, ry)
        os = man(ox, oy, rx, ry)
        # score: prefer smaller our distance; prefer keeping advantage
        # penalize if we worsen our race advantage.
        cur_adv = os - man(sx, sy, rx, ry)
        nxt_adv = os - ns
        adv_delta = nxt_adv - cur_adv
        # also slightly avoid stepping farther from opponent (keeps some separation)
        sep = -man(nx, ny, ox, oy)
        key = (adv_delta, -ns, sep, -abs(nx - sx) - abs(ny - sy))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]