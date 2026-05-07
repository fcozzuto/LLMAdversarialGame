def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    # Predict opponent next move as greedy toward nearest resource.
    def predict_opp_next():
        best = None
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            if d < bestd:
                bestd = d
                best = (nx, ny)
        if best is None:
            return (ox, oy)
        return best

    nox, noy = predict_opp_next()
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Score: maximize our closeness advantage over opponent for remaining resources.
        # Also heavily reward stepping onto a resource.
        val = 0
        if (nx, ny) in res_set:
            val += 10000
        opp_here = nox, noy
        # For each resource: if we are closer than opponent, that helps; if farther, hurts.
        # Use maximum advantage across resources, plus a small tie on average closeness.
        best_adv = -10**9
        sum_self = 0
        sum_opp = 0
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(opp_here[0], opp_here[1], rx, ry)
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
            sum_self += sd
            sum_opp += od
        val += best_adv * 100
        val += (sum_opp - sum_self) / (len(resources) + 1.0)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]