def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    if not res:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        my_near = 10**9
        my_adv_for_best = -10**9
        opp_near_for_best = 10**9

        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            md = dist_cheb(nx, ny, rx, ry)
            od = dist_cheb(ox, oy, rx, ry)

            # Prefer grabbing/being closest; strongly prefer resources where I'm ahead of opponent.
            adv = od - md
            if adv > my_adv_for_best or (adv == my_adv_for_best and (md < my_near or (md == my_near and od < opp_near_for_best))):
                my_adv_for_best = adv
                my_near = md
                opp_near_for_best = od

        # Convert to a single deterministic score.
        # Large weight on being ahead; secondary on closer to the target resource; slight preference for moving.
        move_pref = abs(dx) + abs(dy)
        score = my_adv_for_best * 1000 - my_near * 10 - opp_near_for_best + move_pref * 0.001

        if score > best_score or (score == best_score and (dx, dy) > (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move