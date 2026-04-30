def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        # Drift toward center while avoiding obstacles
        tx, ty = w // 2, h // 2
        best = (10**9, -10**9)
        best_move = [0, 0]
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d_self = abs(nx - tx) + abs(ny - ty)
            d_opp = abs((ox) - nx) + abs((oy) - ny)
            cand = (d_self, d_opp)
            if cand[0] < best[0] or (cand[0] == best[0] and cand[1] > best[1]):
                best = (cand[0], cand[1])
                best_move = [dx, dy]
        return best_move

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Choose resource that we can reach sooner relative to opponent
    best_res = None
    best_adv = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        adv = do - ds  # higher means we are relatively closer
        if adv > best_adv:
            best_adv = adv
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]

    rx, ry = best_res
    best_key = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = dist((nx, ny), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        # primary: reduce distance to target, secondary: keep opponent farther from target
        key = (d_self, -(d_opp))
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_move else [0, 0]