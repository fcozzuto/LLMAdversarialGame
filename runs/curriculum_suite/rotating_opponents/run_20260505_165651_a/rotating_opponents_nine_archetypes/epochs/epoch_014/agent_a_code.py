def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # want ours closer
        dist_center = abs(rx - cx) + abs(ry - cy)
        # reward being able to arrive sooner, slight center bias, deterministic tie-break
        key = (adv, 1.0 / (sd + 1), -dist_center, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myd = man(nx, ny, rx, ry)
        opd = man(ox, oy, rx, ry)

        # Prefer moves that increase race advantage and reduce own distance.
        race = opd - myd
        prog = myd - man(sx, sy, rx, ry)  # negative is good
        # If opponent is very close to the target, prioritize grabbing proximity fast.
        opp_close = (man(ox, oy, rx, ry) <= myd + 1)

        dist_center = abs(nx - cx) + abs(ny - cy)
        val = (race, -myd, -prog, 0.2 if opp_close else 0.0, -dist_center)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]