def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    my_half = sx < w // 2

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx = w - 1 if my_half else 0
        ty = h - 1 if sy <= h // 2 else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # density: count resources within small manhattan radius (deterministic)
    dens = {}
    for rx, ry in resources:
        c = 0
        for x2, y2 in resources:
            if abs(rx - x2) + abs(ry - y2) <= 2:
                c += 1
        dens[(rx, ry)] = c

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        score = -10**18
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d  # bigger => we are closer than opponent after move
            half_bias = 1 if (rx < w // 2) == my_half else -1
            # Prefer staying on/near our half and denser resource clumps
            cand = adv * 100 - self_d * 3 + dens[(rx, ry)] * 2 + half_bias
            if cand > score:
                score = cand
        # tiny deterministic tie-break: prefer moves that reduce manhattan to best cluster centroid approx
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # tie-break with lexicographic on (dx,dy) but deterministic: prefer (dx,dy) closer to our direction (toward target side)
            pref_dir = 1 if my_half else -1
            tb = (abs(dx - pref_dir) + abs(dy))  # smaller better
            cb = (abs(best_move[0] - pref_dir) + abs(best_move[1]))
            if tb < cb:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]