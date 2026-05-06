def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If no resources remain, drift to reduce opponent advantage.
    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestk = None
        for dx, dy, nx, ny in moves:
            k = (man(nx, ny, tx, ty), man(nx, ny, ox, oy), man(nx, ny, sx, sy))
            if bestk is None or k < bestk:
                bestk = k
                best = (dx, dy)
        return [best[0], best[1]]

    # Score resources by whether we can get them earlier than opponent; otherwise we try to deny.
    best_move = (0, 0)
    best_key = None

    # Deterministic "goal" when no immediate win: go to a midpoint-biased cell toward the closest resource.
    midx, midy = (sx + ox) // 2, (sy + oy) // 2

    for dx, dy, nx, ny in moves:
        self_now = man(nx, ny, sx, sy)
        # Evaluate best resource for this candidate move.
        best_res_key = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer cells where we are strictly closer (or at least not behind), strongly.
            # Then prefer shorter ds, and finally prefer resources that are closer to the opponent (deny).
            win_margin = do - ds
            k = (-(1 if win_margin > 0 else 0), -win_margin, ds, -do, rx, ry)
            if best_res_key is None or k < best_res_key:
                best_res_key = k
        # If we can't "win" any resource next step, move toward a midpoint-biased direction to contest mid-grid.
        # Identify whether candidate has any winning resource.
        has_win = False
        for rx, ry in resources:
            if man(nx, ny, rx, ry) < man(ox, oy, rx, ry):
                has_win = True
                break

        # Strongly prefer winning lines; otherwise contest center and also move toward closest resource.
        if has_win:
            key = (0, best_res_key)
        else:
            # Midpoint contest + reduce distance to closest resource
            closest_r = min(resources, key=lambda p: man(nx, ny, p[0], p[1]))
            key = (1, man(nx, ny, midx, midy), man(nx, ny, closest_r[0], closest_r[1]), man(nx, ny, ox, oy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]