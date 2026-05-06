def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    min_opp = None
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if min_opp is None or d < min_opp:
            min_opp = d

    best = None  # (score, self_d, dx, dy)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue

            best_res_score = None
            best_self_d = None
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                denial = 0
                if od == min_opp:
                    denial = 60
                elif od == min_opp + 1:
                    denial = 20
                s = (od - sd) * 18 + denial - sd * 0.5 - (abs(rx - w // 2) + abs(ry - h // 2)) * 0.001
                if best_res_score is None or s > best_res_score or (s == best_res_score and sd < best_self_d):
                    best_res_score = s
                    best_self_d = sd

            if best is None or best_res_score > best[0] or (best_res_score == best[0] and best_self_d < best[1]):
                best = (best_res_score, best_self_d, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]