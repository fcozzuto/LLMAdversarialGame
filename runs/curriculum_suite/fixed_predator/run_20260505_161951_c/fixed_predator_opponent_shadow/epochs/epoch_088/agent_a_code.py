def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (man(nx, ny, tx, ty), man(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Prefer moves that create/extend advantage over the opponent for the best reachable resource.
    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_overall = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer
            # Primary: maximize advantage; Secondary: prefer smaller absolute distance to that resource
            key_r = (adv, -sd)
            if best_overall is None or key_r > best_overall:
                best_overall = key_r
        # Tie-break deterministically: prefer reducing distance to opponent when our advantage is poor.
        opp_d = man(nx, ny, ox, oy)
        overall_key = (best_overall[0], best_overall[1], -opp_d, dx, dy)
        if best is None or overall_key > best[0]:
            best = (overall_key, (dx, dy))
    return [best[1][0], best[1][1]]