def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Choose target resource: prefer one we can reach no later than opponent
    best_target = None
    best_self_dist = None
    opp_dists = {}
    for rx, ry in resources:
        sd = d2(sx, sy, rx, ry)
        od = d2(ox, oy, rx, ry)
        opp_dists[(rx, ry)] = od
        if sd <= od:
            if best_target is None or sd < best_self_dist or (sd == best_self_dist and od > opp_dists[best_target]):
                best_target = (rx, ry)
                best_self_dist = sd
    if best_target is None:
        # fallback: closest resource
        for rx, ry in resources:
            sd = d2(sx, sy, rx, ry)
            if best_target is None or sd < best_self_dist:
                best_target = (rx, ry)
                best_self_dist = sd

    tx, ty = best_target

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        res_dist = d2(nx, ny, tx, ty)
        opp_dist = d2(nx, ny, ox, oy)
        # Prefer smaller resource distance, and (slightly) larger distance from opponent
        score = (-res_dist) + 0.12 * opp_dist
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move