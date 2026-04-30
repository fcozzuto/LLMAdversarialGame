def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose target resource: prefer ones where we are closer than opponent; then maximize (opp_dist - self_dist)
    best = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        pref = (ds <= do, do - ds, -ds)
        if best is None or pref > best[0]:
            best = (pref, rx, ry)
    if best is None:
        # No visible resources: move toward center-ish while avoiding obstacles
        tx, ty = (w // 2, h // 2)
    else:
        _, tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # Greedy: minimize distance to target, but slightly prefer moves that keep away from opponent
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), (ox, oy))
        score = (-(d_t), d_o)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]