def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Target value: how much closer we are than opponent, plus urgency.
        # Denial bonus if we'd arrive strictly earlier than opponent.
        worst_pick = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Encourage immediate collection progress; discourage giving opponent earlier access.
            denial = 2.0 if (sd < od) else (-0.5 if sd > od else -0.1)
            val = (od - sd) + denial + (0.05 * (sd == 0)) + (-0.01 * sd)
            if worst_pick is None or val > worst_pick:
                worst_pick = val

        # With multiple resources, prefer move that maximizes the best-target score,
        # and also slightly prefers staying aligned toward opponent-side resources to contest.
        if worst_pick is None:
            continue
        align = -0.002 * (md(nx, ny, ox, oy))
        total = worst_pick + align

        if best_val is None or total > best_val:
            best_val = total
            best_move = [dx, dy]

    # If all candidate moves were blocked, stay.
    return best_move