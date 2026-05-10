def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    last = None
    sp = observation.get("self_path") or []
    if sp:
        last = tuple(sp[-1])

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        da = a - c
        if da < 0:
            da = -da
        db = b - d
        if db < 0:
            db = -db
        return da + db

    # Find a good global target deterministically (nearest unclaimed that is also not too close to opponent)
    ut = None
    best_t = 10**9
    for cx, cy in unclaimed:
        dme = man(cx, cy, x, y)
        dob = man(cx, cy, ox, oy)
        # Prefer cells that are closer to us but farther from opponent
        key = dme * 3 - min(20, dob)
        if key < best_t:
            best_t = key
            ut = (cx, cy)

    # If no unclaimed exist, attack opponent territory or keep control
    if ut is None:
        ut = (ox, oy) if oppT else (x, y)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))
    moves.append((0, 0))  # deterministic: keep last as fallback

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        md = man(nx, ny, ut[0], ut[1])
        dob = man(nx, ny, ox, oy)

        if (nx, ny) in unclaimed:
            val = 200 - 3 * md + 1.5 * min(16, dob)
        elif (nx, ny) in oppT:
            val = 90 - 2 * md + 0.5 * min(16, dob)
        elif (nx, ny) in selfT:
            val = 20 - md
        else:
            val = 5 - 2 * md

        if last is not None and (nx, ny) == last:
            val -= 8

        # Slightly prefer advancing toward our target over staying
        if (dx, dy) == (0, 0):
            val -= 2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]