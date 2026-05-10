def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    role = str(observation.get("self_role") or "")
    is_evader = ("evad" in role.lower())

    def man(x, y):
        return abs(x - ox) + abs(y - oy)

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in ob:
                m += 1
        return m

    best_dxdy = [0, 0]
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in ob:
            continue

        d = man(nx, ny)
        stay = 1 if (dx == 0 and dy == 0) else 0
        mob = mobility(nx, ny)

        # capture if landing on opponent (radius 0)
        cap = 1 if (nx == ox and ny == oy) else 0

        if is_evader:
            key = (0 if cap else 1, -cap, d, mob, -stay, dx, dy)
            # maximize distance; minimize preference to stay if tied
            key = (-cap, d, mob, -stay, -dx, -dy)
        else:
            key = (0 if cap else 1, -cap, -d, mob, stay, -dx, -dy)
            # maximize capture, minimize distance; prefer not to stay
            key = (-cap, -d, mob, -stay, dx, dy)

        if best_key is None or key < best_key:
            best_key = key
            best_dxdy = [dx, dy]

    return best_dxdy