def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def king_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = (-10**30, -10**30, -10**30)

    for dxm in (-1, 0, 1):
        for dym in (-1, 0, 1):
            nx, ny = sx + dxm, sy + dym
            if not inside(nx, ny) or (nx, ny) in obs:
                continue

            best_adv = -10**30
            best_sd = 10**30
            best_od = -10**30
            any_take = False

            for rx, ry in resources:
                sd = king_dist(nx, ny, rx, ry)
                od = king_dist(ox, oy, rx, ry)
                adv = od - sd
                if adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and od > best_od))):
                    best_adv, best_sd, best_od = adv, sd, od
                if sd <= od:
                    any_take = True

            # Prefer immediate guaranteed races; otherwise push hardest advantage.
            # Also avoid moving into generally worse position vs all resources.
            if any_take and best_adv < 0:
                key = (-10**30, 10**30, -10**30)
            else:
                # Second criterion: be closer to a resource that opponent is farther from.
                close_gain = -10**30
                for rx, ry in resources:
                    sd = king_dist(nx, ny, rx, ry)
                    od = king_dist(ox, oy, rx, ry)
                    if od > sd:
                        g = (od - sd) - sd * 0.01
                        if g > close_gain:
                            close_gain = g
                if close_gain == -10**30:
                    close_gain = -best_sd * 0.01

                key = (best_adv, close_gain, -best_sd)
            if key > best_key:
                best_key = key
                best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]