def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not moves:
        return [0, 0]

    best = None
    best_move = (0, 0)
    res_list = resources if resources else []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if res_list:
            # maximize (opp_dist - my_dist) to the best contested resource
            my_best = 10**9
            opp_best = 10**9
            for rx, ry in res_list:
                md1 = man(nx, ny, rx, ry)
                md2 = man(ox, oy, rx, ry)
                # want smallest my distance, largest opponent advantage handled by score below
                if md1 < my_best:
                    my_best = md1
                if md2 < opp_best:
                    opp_best = md2
            # compute best "race" across all resources
            best_race = -10**9
            for rx, ry in res_list:
                md1 = man(nx, ny, rx, ry)
                md2 = man(ox, oy, rx, ry)
                race = md2 - md1  # positive means I'm closer
                if race > best_race:
                    best_race = race
            # encourage also being generally close to any resource
            val = (best_race * 100) - my_best - (0.1 * man(nx, ny, ox, oy))
        else:
            # no visible resources: move toward center while not walking into opponent
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_dist = abs(nx - cx) + abs(ny - cy)
            opp_dist = man(nx, ny, ox, oy)
            val = (opp_dist * 2) - int(center_dist * 10)

        if best is None or val > best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]