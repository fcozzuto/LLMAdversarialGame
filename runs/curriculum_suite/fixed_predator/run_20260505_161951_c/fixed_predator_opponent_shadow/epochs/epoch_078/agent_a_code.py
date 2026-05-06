def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_d = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = dist(nx, ny, tx, ty)
            if best_d is None or d < best_d or (d == best_d and (dx, dy) < best):
                best_d, best = d, (dx, dy)
        return [best[0], best[1]]

    # Decide whether to contest by chasing opponent (if they are strictly ahead on our nearest resource)
    nearest = min(resources, key=lambda r: dist(sx, sy, r[0], r[1]))
    my_near = dist(sx, sy, nearest[0], nearest[1])
    op_near = dist(ox, oy, nearest[0], nearest[1])
    chase_mode = op_near < my_near

    best = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        if chase_mode:
            # Chase opponent while keeping moves that don't immediately trap us behind obstacles
            key = (dist(nx, ny, ox, oy), dist(nx, ny, nearest[0], nearest[1]))
        else:
            # Maximize advantage: prefer moves where we become closer to some resource than the opponent.
            best_adv = None
            best_my = None
            best_r = None
            for rx, ry in resources:
                my_d = dist(nx, ny, rx, ry)
                op_d = dist(ox, oy, rx, ry)
                adv = my_d - op_d  # lower is better
                if best_adv is None or adv < best_adv or (adv == best_adv and my_d < best_my):
                    best_adv, best_my, best_r = adv, my_d, (rx, ry)
            # Primary: smallest advantage; Secondary: smallest distance to that best resource; Tertiary: keep closer to opponent to reduce their options a bit
            key = (best_adv, best_my, dist(nx, ny, ox, oy))
        if best_key is None or key < best_key or (key == best_key and (dx, dy) < best):
            best_key, best = key, (dx, dy)

    return [best[0], best[1]]