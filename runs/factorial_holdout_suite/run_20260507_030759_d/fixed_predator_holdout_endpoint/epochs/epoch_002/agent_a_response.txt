def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_key = None

    # Choose target resource that is good for us and bad for opponent to reach first
    best_target = None
    best_tkey = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Primary: ensure we are closer than opponent; then maximize margin; then be fast to collect
        tkey = (do - ds, -ds, rx, ry)
        if best_tkey is None or tkey > best_tkey:
            best_tkey = tkey
            best_target = (rx, ry)

    if best_target is None:
        # No reachable known resources (or all blocked): head toward opponent to contest
        tx, ty = ox, oy
    else:
        tx, ty = best_target

    opp_dist_to_target = man(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)

        # We want to reduce our distance to target, while also keeping/creating disadvantage for opponent.
        # If we can't reach target soon, drift toward reducing opponent's best options by moving away from their direction.
        opp_d = man(ox, oy, tx, ty)
        advantage = opp_d - d  # larger means we're closer relative to opponent
        # Extra shaping: avoid stepping so that opponent becomes closer to the same target than we are
        contest_penalty = max(0, d - opp_d)

        # Prefer diagonal progress, but deterministically break ties
        step_cost = abs(dx) + abs(dy)
        key = (advantage, -d, -step_cost, -contest_penalty, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move