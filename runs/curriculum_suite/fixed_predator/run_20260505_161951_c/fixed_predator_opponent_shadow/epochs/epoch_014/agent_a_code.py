def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        bestd = -10**18
        for dx, dy, nx, ny in moves:
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose target: prefer resources where we are "in the race" (opponent closer gives us advantage if we move now)
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        race = od - sd  # positive => opponent is closer (we're behind); prefer targets where we can improve fastest
        # key: primarily maximize immediate race improvement potential, then closeness
        # incorporate a mild anti-opponent pressure: prefer resources far from opponent when tied
        key = (race, -od, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    best_move = None
    best_val = None
    for dx, dy, nx, ny in moves:
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)  # opponent stays this turn; deterministic heuristic
        # Value: strongly minimize distance to our chosen target.
        # If we can become closer than opponent to the target, prioritize it.
        win = od2 - sd2
        # Also lightly prefer moves that reduce distance to opponent to contest when behind.
        key = (-sd2, -(win), man(nx, ny, ox, oy))
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]