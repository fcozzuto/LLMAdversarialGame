def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestm = [0, 0]
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = dist(nx, ny, tx, ty) + 0.001 * dist(nx, ny, ox, oy)
            if best is None or d < best:
                best = d
                bestm = [mx, my]
        return bestm if best is not None else [0, 0]

    best = None
    bestm = [0, 0]
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # After our move, choose the resource giving us maximum "race advantage".
        # Prefer being closer even if the opponent is also close.
        best_adv = None
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            if myd == 0:
                adv = 10_000  # immediate pickup
            else:
                adv = (opd - myd) * 1000 - myd  # deny by losing race, reward by beating race
            # small deterministic tie-break favoring nearer target index/order
            adv -= (rx * 17 + ry * 31) * 0.000001
            if best_adv is None or adv > best_adv:
                best_adv = adv

        # Also slightly penalize stepping away from current best prospects.
        step_r = min(dist(nx, ny, r[0], r[1]) for r in resources)
        val = best_adv - step_r * 0.01

        if best is None or val > best:
            best = val
            bestm = [mx, my]

    return bestm