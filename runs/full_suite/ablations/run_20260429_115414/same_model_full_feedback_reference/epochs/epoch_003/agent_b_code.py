def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    res_set = set(tuple(p) for p in resources)
    opp_next = set()
    for dx, dy in moves:
        px, py = ox + dx, oy + dy
        if inb(px, py) and (px, py) not in obstacles:
            opp_next.add((px, py))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        reward = 0
        if (nx, ny) in res_set:
            reward += 1200
        # Prefer states where we are closer than opponent, and where opponent can't immediately take resources.
        local = 0
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd  # positive => we are closer
            # If opponent can capture that resource next turn, penalize unless we also move onto it.
            if (rx, ry) in opp_next and (nx, ny) != (rx, ry):
                adv -= 8
            local += adv * 10 - myd * 1 + (opd - myd > 0) * 2
        # Also nudge toward reducing distance to nearest resource.
        if resources:
            dmin = min(man(nx, ny, rx, ry) for rx, ry in resources)
            local += 30 - dmin * 3
        # Deterministic tie-break: prefer smallest dx, then dy, for equal value.
        key = (reward + local, -man(nx, ny, ox, oy), -nx, -ny, -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]
    return best_move