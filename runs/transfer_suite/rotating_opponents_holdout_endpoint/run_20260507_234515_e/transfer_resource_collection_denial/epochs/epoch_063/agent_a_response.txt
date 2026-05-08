def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    dirs = (-1, 0, 1)
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Urgency: closer to end, prioritize immediate "capture-first" advantage.
    try:
        tr = int(turns_remaining)
    except:
        tr = 0
    urgency = 1.0 + (max(0, 64 - tr) / 64.0)

    best = None
    best_val = -10**18
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            self_next = (nx, ny)

            # Evaluate by top-2 capture advantages against any resource from this next cell.
            # Advantage is positive when we can arrive no later than opponent (tie favors us via >0).
            advs = []
            for rx, ry in res:
                s_d = dist(self_next, (rx, ry))
                o_d = dist((ox, oy), (rx, ry))
                adv = (o_d - s_d) * urgency
                advs.append(adv)
            advs.sort(reverse=True)
            top = advs[0] + (advs[1] if len(advs) > 1 else 0.0)
            # Secondary term: reduce total distance to the "best" target to avoid dithering.
            best_target = res[0]
            if len(advs) > 0:
                # Find resource achieving max advantage for this move (deterministic tie-break by min dist then coord).
                max_adv = -10**18
                for rx, ry in res:
                    s_d = dist(self_next, (rx, ry))
                    o_d = dist((ox, oy), (rx, ry))
                    adv = (o_d - s_d) * urgency
                    if adv > max_adv or (adv == max_adv and (s_d, rx, ry) < (dist(self_next, best_target), best_target[0], best_target[1])):
                        max_adv = adv
                        best_target = (rx, ry)
            slack = dist(self_next, best_target)
            val = top - 0.01 * slack + 0.0001 * (nx - sx) - 0.0001 * (ny - sy)
            if val > best_val:
                best_val = val
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]