def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Strategy: pick the move that maximizes our competitive advantage for the best reachable resource.
    # Value favors states where we are closer than opponent; tie-breaker favors smaller distance-to-resource.
    best_move = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            nx, ny = x, y
        if cell_blocked(nx, ny):
            nx, ny = x, y

        best_tv = None
        for rx, ry in resources:
            d_me = abs(rx - nx) + abs(ry - ny)
            d_opp = abs(rx - ox) + abs(ry - oy)
            lead = d_opp - d_me
            tv = lead * 1000 - d_me + (d_opp * 0.01)
            if best_tv is None or tv > best_tv or (tv == best_tv and (d_me, d_opp) < best_td):
                best_tv = tv
                best_td = (d_me, d_opp)

        if best_val is None or best_tv > best_val or (best_tv == best_val and (dx, dy) < best_move):
            best_val = best_tv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]