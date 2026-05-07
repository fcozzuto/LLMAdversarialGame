def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_list = [tuple(r) for r in resources]
    res_list.sort()

    if not res_list:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best = (-(10**9), -(10**9), 10**9, (0, 0))
    tr = observation.get("turns_remaining", 1)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        reach_self = 0
        margin_best = -(10**9)
        closest_self = 10**9
        for rx, ry in res_list:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            if ds <= tr:
                if do > ds:
                    reach_self += 1
                    m = do - ds
                    if m > margin_best:
                        margin_best = m
                    if ds < closest_self:
                        closest_self = ds
                else:
                    if ds < closest_self:
                        closest_self = ds
        if reach_self == 0:
            # Fallback: move toward the resource that minimizes (opponent - self) after move.
            # This breaks ties deterministically toward earlier opportunities.
            target = res_list[0]
            best_adv = -(10**9)
            for rx, ry in res_list:
                ds = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                adv = do - ds
                if adv > best_adv or (adv == best_adv and (rx, ry) < target):
                    best_adv = adv
                    target = (rx, ry)
            reach_self = 0
            margin_best = best_adv
            closest_self = dist(nx, ny, target[0], target[1])

        key = (reach_self, margin_best, -closest_self, (nx, ny))
        if key > best[:4]:
            best = (key[0], key[1], -key[2], (dx, dy))

    return [best[3][0], best[3][1]]