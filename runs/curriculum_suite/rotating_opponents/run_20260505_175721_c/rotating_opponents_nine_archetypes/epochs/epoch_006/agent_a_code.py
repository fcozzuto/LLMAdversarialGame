def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestd = 10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = dist(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = [dx, dy]
        return best

    center_bias = 0.15
    best_move = [0, 0]
    best_adv = -10**9
    best_selfd = 10**9

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue

            # Choose resource where we have the largest "reach advantage"
            # advantage = opp_dist - self_dist (bigger is better)
            adv = -10**9
            selfd_for_best = 10**9
            for rx, ry in resources:
                sd = dist(nx, ny, rx, ry)
                od = dist(ox, oy, rx, ry)
                a = od - sd
                if a > adv or (a == adv and sd < selfd_for_best):
                    adv = a
                    selfd_for_best = sd

            # If we can't beat the opponent (adv <= 0), still prefer closest resource.
            # Add slight center bias to break ties deterministically.
            cd = dist(nx, ny, w // 2, h // 2)
            score_adv = adv - center_bias * cd

            if score_adv > best_adv or (score_adv == best_adv and (selfd_for_best, cd) < (best_selfd, dist(best_move[0]+sx, best_move[1]+sy, w//2, h//2))):
                best_adv = score_adv
                best_selfd = selfd_for_best
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]