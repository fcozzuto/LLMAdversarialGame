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

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target scoring: maximize (opponent advantage) and closeness for us; also emphasize denial when opponent is closer.
    best_move = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_r = None
        best_r_key = None
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # denial: if opponent is closer, strongly prefer rushing that resource
            deny = 1 if od < sd else 0
            adv = od - sd  # positive means we are closer than opponent
            # key: higher adv/denial first -> convert to min by negating
            key = (-adv, -deny, sd, od, rx, ry)
            if best_r_key is None or key < best_r_key:
                best_r_key, best_r = key, (rx, ry)
        # Move tie-breakers: prefer moves that also reduce distance to opponent when we are contesting
        contest = 0
        if best_r is not None:
            rx, ry = best_r
            contest = 1 if (abs(ox - rx) + abs(oy - ry)) < (abs(nx - rx) + abs(ny - ry)) else 0
        move_key = (best_r_key, abs(nx - ox) + abs(ny - oy), -contest, nx, ny, dx, dy)
        if best_key is None or move_key < best_key:
            best_key, best_move = move_key, (dx, dy)
    return [best_move[0], best_move[1]]