def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**9, (0, 0))
    if not resources:
        # deterministic roaming toward farthest corner from opponent, but still staying inbounds
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = corners[0]
        bestc = -1
        for c in corners:
            d = cheb(c[0], c[1], ox, oy)
            if d > bestc:
                bestc = d
                tx, ty = c
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = cheb(nx, ny, tx, ty) * -1 + cheb(nx, ny, ox, oy) * 0.05
            if score > best[0]:
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # Resource race: maximize our advantage while discouraging giving the opponent a cleaner approach.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # our best "win" resource in this next position
        my_best_adv = -10**9
        my_best_dist = 10**9
        opp_closest_dist_to_any = 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            if adv > my_best_adv:
                my_best_adv = adv
                my_best_dist = my_d
            elif adv == my_best_adv and my_d < my_best_dist:
                my_best_dist = my_d
            od_any = cheb(ox, oy, rx, ry)
            if od_any < opp_closest_dist_to_any:
                opp_closest_dist_to_any = od_any

        # Intercept fallback: if no clear advantage, move to reduce our distance to opponent resources most closely contested.
        # Also prefer not moving away from the overall front.
        opp_d_center = cheb(nx, ny, ox, oy)
        score = my_best_adv * 100 - my_best_dist * 2 - (opp_closest_dist_to_any - cheb(ox, oy, ox, oy)) * 0 + opp_d_center * -0.05
        if score > best[0]:
            best = (score, (dx, dy))

    return [best[1][0], best[1][1]]