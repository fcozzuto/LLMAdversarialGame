def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    res = [(int(x), int(y)) for x, y in resources]

    # Precompute: for each resource, how close opponent can get in one move (best-case)
    opp_best_next = {}
    for tx, ty in res:
        best = 10**9
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < best:
                best = d
        if best == 10**9:
            best = man(ox, oy, tx, ty)
        opp_best_next[(tx, ty)] = best

    best_move = (0, 0)
    best_score = -10**18

    # Choose the move that maximizes (opponent next closeness advantage over us)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Small obstacle penalty to avoid getting boxed in
        penalty = 0
        for ax, ay in [(nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)]:
            if (ax, ay) in obstacles:
                penalty += 1

        local_best = -10**18
        for tx, ty in res:
            self_d = man(nx, ny, tx, ty)
            opp_next = opp_best_next[(tx, ty)]
            # Margin: bigger means opponent is farther than their best-case next-step distance vs our distance
            margin = opp_next - self_d
            # Encourage closer targets and avoid giving opponent immediate advantage
            sc = margin * 100 - self_d - penalty
            if sc > local_best:
                local_best = sc

        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]