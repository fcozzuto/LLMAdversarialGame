def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target_row = oy if 0 <= oy < h else sy

    # Pick the move that most improves our ability to secure a resource,
    # while also aligning with the opponent's row sweep tendency.
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Row alignment (deterministic bias for sweep_rows archetype)
        align = -2 * abs(ny - target_row)

        # Interception gain over the single best resource for this move
        best_gain_for_move = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer contesting resources that are on/near the opponent's sweep row
            row_match = 2 if ry == target_row else 0
            gain = (od - sd) + row_match - 0.02 * sd
            if gain > best_gain_for_move:
                best_gain_for_move = gain

        val = align + 5 * best_gain_for_move - 0.01 * man(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move