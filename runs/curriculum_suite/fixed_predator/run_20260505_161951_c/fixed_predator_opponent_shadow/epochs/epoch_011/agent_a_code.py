def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

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

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Run away from opponent
        bx, by, best = sx, sy, -10**18
        for dx, dy, nx, ny in moves:
            d = man(nx, ny, ox, oy)
            if d > best:
                best = d
                bx, by = dx, dy
        return [bx, by]

    # Choose target deterministically: best advantage over opponent, else closest to improve.
    best_t, best_adv, best_sd = resources[0], -10**18, 10**18
    for r in resources:
        rx, ry = r
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and (sd < best_sd)):
            best_adv, best_sd, best_t = adv, sd, r

    tx, ty = best_t
    # Evaluate 1-step actions: pick move that reduces our distance to chosen target,
    # with tie-breakers toward blocking (increasing opponent distance to target).
    best_move = (0, 0)
    best_key = None
    for dx, dy, nx, ny in moves:
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # Prefer decreasing our distance; if both equal, prefer increasing opponent distance.
        # Also add slight bias to reduce distance to any favorable resource if target is contested.
        key = (sd2, -od2)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]