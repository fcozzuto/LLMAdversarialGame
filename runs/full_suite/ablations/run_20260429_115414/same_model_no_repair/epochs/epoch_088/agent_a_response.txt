def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = {(p[0], p[1]) for p in obstacles}
    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    res_sorted = sorted(res)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Evaluate this move by how much closer we can get to some resource compared to the opponent.
        best_for_move = None
        best_res = None
        for rx, ry in res_sorted:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Primary: maximize advantage (opd - myd).
            # Secondary: prefer smaller myd among equal advantage.
            # Tertiary: deterministic tie-break by resource order.
            adv = opd - myd
            val = (adv, -myd, -rx, -ry)

            if best_for_move is None or val > best_for_move:
                best_for_move = val
                best_res = (rx, ry)

        # Encourage not getting stuck: slight penalty for being farther from the chosen best resource.
        adv, neg_myd, _, _ = best_for_move
        score = (adv, neg_myd, nx - sx, ny - sy)
        if best_val is None or score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]