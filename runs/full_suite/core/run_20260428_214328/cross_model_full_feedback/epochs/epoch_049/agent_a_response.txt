def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Prefer resources that are closer to us, and farther from opponent (deny).
    # Also prefer moves that reduce our best target distance.
    res = resources
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        if res:
            my_best = 10**9
            opp_best = 10**9
            best_target_score = -10**18
            for rx, ry in res:
                d_my = dist((nx, ny), (rx, ry))
                if d_my < my_best:
                    my_best = d_my
                d_opp = dist((ox, oy), (rx, ry))
                if d_opp < opp_best:
                    opp_best = d_opp
                # Score: get it soon, deny opponent by making it far from them.
                # If opponent is already close, penalize more.
                denom = 1 + d_my
                deny = d_opp
                tscore = (1000 / denom) + 0.25 * deny - (4.0 / (1 + max(0, d_opp - d_my)))
                if tscore > best_target_score:
                    best_target_score = tscore

            # Additional shaping: if opponent is closer to our nearest target, switch by punishing.
            nearest = my_best
            opp_to_nearest = 10**9
            for rx, ry in res:
                if dist((nx, ny), (rx, ry)) == nearest:
                    opp_to_nearest = min(opp_to_nearest, dist((ox, oy), (rx, ry)))
            danger = 0.0
            if opp_to_nearest < nearest:
                danger = 10.0 * (nearest - opp_to_nearest)
            val = best_target_score - danger
        else:
            # No visible resources: move toward the center to increase chance to meet resources later.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = -dist((nx, ny), (cx, cy)) - 0.1 * dist((ox, oy), (nx, ny))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]