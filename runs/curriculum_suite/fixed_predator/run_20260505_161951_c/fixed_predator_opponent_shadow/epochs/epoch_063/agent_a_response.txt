def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy, nx, ny in valid:
            key = (man(nx, ny, tx, ty), -man(nx, ny, ox, oy))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_key = None
    for dx, dy, nx, ny in valid:
        # Primary: deny opponent access via distance advantage to our next target.
        # Secondary: ensure we can reach it sooner.
        best_adv = None
        best_self = None
        best_opp = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if (best_adv is None or
                adv > best_adv or
                (adv == best_adv and sd < best_self) or
                (adv == best_adv and sd == best_self and od > best_opp)):
                best_adv, best_self, best_opp = adv, sd, od
        key = (-best_adv, best_self, -best_opp, abs(nx - ox) + abs(ny - oy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]