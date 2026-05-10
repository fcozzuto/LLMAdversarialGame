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

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        adv = do - ds  # positive => we are closer
        # Opponent archetype: sweep_rows; contest their current row if possible.
        row_contest = 2 if ry == oy else 0
        # Minor preference for nearer targets to reduce dithering.
        key = (-adv - row_contest * 0.5, ds + (0 if ry == oy else 0.2), rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry), adv, row_contest)

    tx, ty = best[1]

    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dtx = abs(tx - nx) + abs(ty - ny)
        # If we're contesting opponent's row, bias towards stepping onto that row early.
        row_bias = 0
        if ty == oy:
            row_bias = 0 if ny == oy else 1
        key = (dtx + row_bias, abs(dx) + abs(dy), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]