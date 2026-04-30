def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if (nx, ny) not in obstacles:
                        yield dx, dy, nx, ny

    # If no resources, drift toward center to reduce opponent advantage slightly
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (10**9, 0, 0)
        for dx, dy, nx, ny in neighbors(sx, sy):
            score = (abs(nx - cx) + abs(ny - cy),)
            if score < best[0:1] + best[1:2]:
                best = (score[0], dx, dy)
        return [best[1], best[2]]

    # Choose a resource that maximizes how much closer we are than opponent
    best_res = None
    best_adv = -10**9
    best_self_d = 10**9
    for r in resources:
        rx, ry = r
        ds = max(0, dist((sx, sy), (rx, ry)))
        do = max(0, dist((ox, oy), (rx, ry)))
        adv = do - ds  # positive means we are closer
        if adv > best_adv or (adv == best_adv and ds < best_self_d):
            best_adv = adv
            best_self_d = ds
            best_res = (rx, ry)

    tx, ty = best_res

    # Move one step toward target, but also discourage stepping into opponent's immediate reach
    # Immediate reach as Manhattan within 2 (deterministic, cheap)
    def opp_reach(nx, ny):
        return dist((ox, oy), (nx, ny)) <= 2

    candidates = []
    for dx, dy, nx, ny in neighbors(sx, sy):
        d_to_t = dist((nx, ny), (tx, ty))
        d_self = dist((sx, sy), (tx, ty))
        # Prefer reducing distance to target; avoid opponent reach; prefer staying if equally good
        penalty = 1000 if opp_reach(nx, ny) else 0
        # Slight preference for moves that also increase distance from opponent
        opp_d = dist((nx, ny), (ox, oy))
        cur_opp_d = dist((sx, sy), (ox, oy))
        opp_gain = opp_d - cur_opp_d
        score = (penalty, d_to_t, -opp_gain, abs(dx) + abs(dy), dx == 0 and dy == 0)
        candidates.append((score, dx, dy))
    candidates.sort()
    _, dx, dy = candidates[0]
    return [dx, dy]