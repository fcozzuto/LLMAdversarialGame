def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = -10**18

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

            # Advantaged target: maximize (opp_dist - my_dist) for the closest advantageous resource.
            # Tie-break: prefer moving closer to center if no strong advantage.
            my_best = 10**9
            opp_best = 10**9
            adv_best = -10**9

            # Deterministic iteration order
            for rx, ry in sorted(resources, key=lambda t: (t[0], t[1])):
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                adv = od - md
                if adv > adv_best:
                    adv_best = adv
                if md < my_best:
                    my_best = md
                if od < opp_best:
                    opp_best = od

            center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))  # higher is better
            score = 1000 * adv_best - 10 * my_best + 0.5 * opp_best + center_bias * 0.01

            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    else:
        # No visible resources: head toward center while avoiding obstacles
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            score = -dist
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]