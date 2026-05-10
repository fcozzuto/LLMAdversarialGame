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

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    # Deterministic tie-breaking order: prefer orthogonal/forward moves slightly
    # by adding a tiny "dir_rank" to the evaluation.
    dir_rank = {}
    r = 0
    for dx, dy in dirs:
        dir_rank[(dx, dy)] = r
        r += 1

    best = None
    best_val = -10**18

    remaining = observation.get("remaining_resource_count", len(resources))
    rem_bias = 1.0 / (1 + remaining)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose the resource that maximizes our relative progress from (nx,ny).
        best_cell_val = -10**18
        for rpos in resources:
            if rpos is None or len(rpos) < 2:
                continue
            rx, ry = rpos[0], rpos[1]
            if (rx, ry) in obstacles:
                continue

            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Primary: how much closer we are than opponent.
            # Secondary: avoid giving opponent an immediate capture (od small).
            # Tertiary: slightly prefer nearer resources to reduce travel.
            rel = od - sd
            capture_risk = (0 if od > 1 else 2)
            travel = -0.15 * sd
            val = (rel * 10.0) - (capture_risk * 6.0) + travel + (rem_bias * rel)

            # If tied, prefer closer to reduce variance.
            if val > best_cell_val:
                best_cell_val = val

        # If no resource was valid, stay.
        if best_cell_val == -10**18:
            continue

        # Final deterministic tie-break: smaller dir_rank.
        val2 = best_cell_val - dir_rank[(dx, dy)] * 1e-6
        if val2 > best_val:
            best_val = val2
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]