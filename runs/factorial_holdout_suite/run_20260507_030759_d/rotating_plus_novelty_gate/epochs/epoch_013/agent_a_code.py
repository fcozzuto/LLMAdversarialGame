def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        # Evaluate each move by the best "steal advantage" we can get on next position.
        # Advantage = (opponent distance to resource) - (our distance to resource).
        best_move = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            local_best = -10**9
            local_tiebreak = 10**9
            # Consider resources deterministically: sort by (dist, x, y)
            res_sorted = sorted(resources, key=lambda r: (man(nx, ny, r[0], r[1]), r[0], r[1]))
            # Limit scan to keep deterministic and fast
            for r in res_sorted[:6]:
                rx, ry = r
                our_d = man(nx, ny, rx, ry)
                opp_d = man(ox, oy, rx, ry)
                adv = opp_d - our_d
                if adv > local_best or (adv == local_best and our_d < local_tiebreak):
                    local_best = adv
                    local_tiebreak = our_d
            key = (-(local_best), local_tiebreak, abs((sx + dx) - ox), abs((sy + dy) - oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # If no visible resources, drift toward opponent's x-channel then toward opponent.
    target_x = w - 1 if sy % 2 == 0 else 0
    # Also bias y toward opponent to reduce time-to-contest.
    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        key = (abs(nx - target_x), abs(ox - nx), abs(ny - oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]