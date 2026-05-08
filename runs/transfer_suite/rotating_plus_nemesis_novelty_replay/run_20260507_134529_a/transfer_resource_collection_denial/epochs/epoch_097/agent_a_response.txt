def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # If no resources, head toward center while slightly biasing away from opponent.
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = man(nx, ny, tx, ty) + 0.2 * man(nx, ny, ox, oy)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    # Interception-capable: maximize advantage (opponent_distance - my_distance_after_move).
    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate best resource from this potential position.
        best_adv = None
        best_myd = None
        best_oppd = None
        for rx, ry in resources:
            myd1 = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd1
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_myd is None or myd1 < best_myd)) or \
               (adv == best_adv and myd1 == best_myd and (opd < best_oppd)):
                best_adv, best_myd, best_oppd = adv, myd1, opd
        # Prefer taking/contesting resources where we're closer; if not possible, minimize being behind.
        key = (best_adv, -best_oppd, -best_myd)
        if best_key is None or key > best_key or (key == best_key and (dx, dy) < (best_move[0], best_move[1])):
            best_key = key
            best_move = [dx, dy]
    return best_move