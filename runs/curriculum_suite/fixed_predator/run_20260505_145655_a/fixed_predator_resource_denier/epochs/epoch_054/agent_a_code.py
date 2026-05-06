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

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue

        # For this candidate next cell, pick the best resource to deny.
        step_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            denial = od - sd
            # prefer being (or staying) closer than opponent; also prefer shorter path
            score = denial * 12 - sd * 2
            # slight center bias to stabilize
            score += -(((rx - cx) ** 2 + (ry - cy) ** 2) * 0.0002)
            # tie-break deterministically by coordinates
            t = (score, -abs(rx - nx) - abs(ry - ny), -rx, -ry)
            if step_best is None or t > step_best[0]:
                step_best = (t, sd, denial, rx, ry)

        if step_best is None:
            continue
        t, sd, denial, rx, ry = step_best

        # If we can reach a resource that opponent is far from, prioritize it strongly.
        reach_boost = 0
        if sd == 0:
            reach_boost += 50
        elif sd == 1:
            reach_boost += 18

        # Keep moves that improve our ability to be in front of opponent.
        cur_best_den = max((man(sx, sy, rx, ry), man(ox, oy, rx, ry)) for rx, ry in resources)
        # cur_best_den[1] is opponent dist for some resource; use average-ish proxy instead:
        # (deterministic, cheap) compare to best denial among resources from current pos.
        cur_den = max((man(ox, oy, rx, ry) - man(sx, sy, rx, ry)) for rx, ry in resources)
        improve = denial - cur_den * 0.1

        total = t[0] + reach_boost + improve * 3 + (1 if denial > 0 else 0)
        if best_score is None or (total, -abs(dx), -abs(dy), dx, dy) > best_score:
            best_score = (total, -abs(dx), -abs(dy), dx, dy)
            best_move = [dx, dy]

    return best_move