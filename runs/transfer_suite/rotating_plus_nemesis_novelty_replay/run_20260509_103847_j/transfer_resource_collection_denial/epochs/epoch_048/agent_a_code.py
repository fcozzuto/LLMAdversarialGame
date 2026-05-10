def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy))
    if not valid_moves:
        return [0, 0]

    if not resources:
        return [0, 0]

    best_r = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        immediate = 0 if ds <= 1 else 1
        avoid_sweep = 0 if ry != oy else 1  # opponent likely sweeps along its current row
        key = (immediate, avoid_sweep, do - ds, ds, rx, ry)
        if best_r is None or key < best_r[0]:
            best_r = (key, (rx, ry))
    tx, ty = best_r[1]

    best_move = None
    best_val = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        d_to_target = man(nx, ny, tx, ty)
        # prefer closer to target; break ties to reduce opponent's chance
        opp_dist = man(ox, oy, tx, ty)
        val = (d_to_target, -((opp_dist - man(nx, ny, tx, ty)) > 0), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]