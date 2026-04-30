def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick best target resource to race for (deterministic scoring).
    if resources:
        best = None
        best_score = -10**9
        for rx, ry in resources:
            dS = dist((sx, sy), (rx, ry))
            dO = dist((ox, oy), (rx, ry))
            # Prefer resources where we are closer than opponent; add slight bias toward smaller dS.
            score = (dO - dS) * 100 - dS
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources: drift toward a stable central point.
        tx, ty = (w // 2, h // 2)

    # Choose move that (1) approaches target, (2) avoids obstacles, (3) considers opponent pressure.
    opp_d_now = dist((ox, oy), (sx, sy))
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = dist((nx, ny), (tx, ty))
        d_to_opp = dist((nx, ny), (ox, oy))
        # Higher is better.
        val = -d_to_target * 10 + d_to_opp
        # Small preference to not move into being closer to opponent if currently too close.
        if opp_d_now <= 2:
            val += (d_to_opp - opp_d_now) * 2
        # Deterministic tie-break: prefer non-stay then lexicographic.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Prefer moves that change position; then lexicographic dx,dy.
            if best_move == (0, 0) and (dx, dy) != (0, 0):
                best_move = (dx, dy)
            elif (dx, dy) != (0, 0) and ((dx, dy) < best_move):
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]