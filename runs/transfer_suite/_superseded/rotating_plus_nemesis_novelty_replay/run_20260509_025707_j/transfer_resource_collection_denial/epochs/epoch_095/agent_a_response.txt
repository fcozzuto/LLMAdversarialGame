def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Interception-style: maximize (opponent_dist - self_dist) over resources after this move.
    # This prefers being able to reach (or be close to) a resource before the sweeper.
    best_move = [0, 0]
    best_val = -10**18
    best_tie = 10**18

    # Extra deterministic bias: align with opponent's sweep line (row/column) when it doesn't hurt interception.
    prefer_row = oy if 0 <= oy < h else sy
    prefer_col = ox if 0 <= ox < w else sx

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_adv = -10**18
        closest_self = 10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            if adv > best_adv:
                best_adv = adv
            if sd < closest_self:
                closest_self = sd

        # If we can clearly win a resource soon, prioritize that decisively.
        sweep_bias = -abs(ny - prefer_row) * 0.001 - abs(nx - prefer_col) * 0.001
        val = best_adv + sweep_bias

        # Tie-break: smaller own distance to the best-advantaged resource class, then deterministic coordinate.
        if val > best_val or (val == best_val and (closest_self < best_tie or (closest_self == best_tie and (dx, dy) < tuple(best_move)))):
            best_val = val
            best_tie = closest_self
            best_move = [dx, dy]

    return best_move