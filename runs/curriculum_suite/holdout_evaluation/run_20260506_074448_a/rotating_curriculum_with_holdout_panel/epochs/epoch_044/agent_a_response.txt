def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def center_bias(x, y):
        dx, dy = x - cx, y - cy
        return -0.002 * (dx * dx + dy * dy)

    # Predict opponent's nearest-resource target (nearest_resource archetype).
    opp_target = None
    opp_td = 10**9
    for (rx, ry) in resources:
        if (rx, ry) in obstacles:
            continue
        d = man(ox, oy, rx, ry)
        if d < opp_td:
            opp_td = d
            opp_target = (rx, ry)

    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Advantage over opponent for grabbing any resource.
        best_adv = -10**9
        my_nearest = 10**9
        for (rx, ry) in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - myd
            if adv > best_adv:
                best_adv = adv
            if myd < my_nearest:
                my_nearest = myd

        my_to_opp_target = 10**9
        if opp_target is not None:
            my_to_opp_target = man(nx, ny, opp_target[0], opp_target[1])

        # Interception term: how much closer we are than opponent to their predicted target.
        intercept = (opp_td - my_to_opp_target) if opp_target is not None else 0

        # Penalize being closer to opponent in a way that helps their pursuit; still allow contesting.
        opp_dist = man(nx, ny, ox, oy)

        score = (best_adv * 10.0) + (intercept * 6.0) - (my_nearest * 0.35) - (opp_dist * 0.08) + center_bias(nx, ny)

        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]