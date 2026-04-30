def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources_list = list(resources)
    best = None
    best_val = -10**30

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            val = -10**29
        else:
            val = 0.0
            if (nx, ny) in resources:
                val += 100000.0
            if resources_list:
                d_self = cheb(nx, ny, ox, oy)  # proxy for "pressure" on center
                val += -0.1 * d_self

                # Focus on best "swing": go where you're not behind (or can steal)
                my_best = 10**9
                opp_best = 10**9
                for rx, ry in resources_list:
                    if (rx, ry) in obstacles:
                        continue
                    ds = cheb(nx, ny, rx, ry)
                    do = cheb(ox, oy, rx, ry)
                    if ds < my_best: my_best = ds
                    if do < opp_best: opp_best = do
                    # contested bonus/penalty
                    if ds <= do:
                        val += 40.0 / (1 + ds)
                    else:
                        val += -30.0 / (1 + ds) * 0.6
                    # prioritize close resources with distance gap
                    gap = do - ds
                    val += 6.0 * gap / (1 + ds)  # positive when stealing/keeping ahead

                val += -3.0 * my_best
                val += 1.0 * max(0, opp_best - my_best)

            # Mild anti-collision / pursuit blocking
            val += -0.05 * cheb(nx, ny, ox, oy)
            if resources_list:
                # Prefer moving away if opponent is already much closer to all remaining resources
                # (helps avoid deadlocks near contested areas)
                my_to_nearest = 10**9
                opp_to_nearest = 10**9
                for rx, ry in resources_list:
                    my_to_nearest = min(my_to_nearest, cheb(nx, ny, rx, ry))
                    opp_to_nearest = min(opp_to_nearest, cheb(ox, oy, rx, ry))
                val += -2.5 * max(0, opp_to_nearest - my_to_nearest)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]