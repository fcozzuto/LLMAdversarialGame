def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    res_set = set(tuple(p) for p in resources)

    # Pick a target that we can reach no later than (or sooner than) the opponent, otherwise the one we approach fastest.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Primary: we want do - ds large (we closer). Secondary: prefer targets that are reachable soon and not blocked by trivial distance.
        # Tertiary: deterministic preference by coordinate.
        key = (-(do - ds), ds, rx, ry)  # smaller is better because we negate advantage
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        adv2 = do2 - ds2  # positive => we are closer than opponent to the same target
        collect = 1 if (nx, ny) in res_set else 0
        # Small tie-break toward reducing our distance; staying on target collection is prioritized.
        score = (collect * 1000) + adv2 * 10 - ds2
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]