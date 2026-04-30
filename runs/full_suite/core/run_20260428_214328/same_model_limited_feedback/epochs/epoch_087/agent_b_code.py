def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    center_bias = 0.02

    # Pick a target resource where we are not worse than the opponent; otherwise pick nearest to us.
    best_adv = None
    best_adv_key = None
    best_any = None
    best_any_d = None
    for r in resources:
        rd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        cb = -((r[0] - cx) ** 2 + (r[1] - cy) ** 2)
        key_any = (rd, -od, cb)
        if best_any_d is None or rd < best_any_d:
            best_any_d = rd
            best_any = r
        if rd <= od:
            key_adv = (rd, -od, cb)
            if best_adv_key is None or key_adv < best_adv_key:
                best_adv_key = key_adv
                best_adv = r
    target = best_adv if best_adv is not None else best_any

    # Evaluate candidate moves with deterministic scoring; avoid obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is None:
            # Fallback: drift toward center while keeping away from opponent.
            nearest_r = min(resources, key=lambda r: dist((nx, ny), r)) if resources else (sx, sy)
            tdist = dist((nx, ny), nearest_r)
        else:
            tdist = dist((nx, ny), target)
        opp_d = dist((nx, ny), (ox, oy))

        # Secondary: encourage moving closer to a resource that is currently closer for us than for the opponent.
        adv_score = 0.0
        for r in resources:
            if r == target:
                continue
            d1 = dist((nx, ny), r)
            d2 = dist((ox, oy), r)
            if d1 <= d2:
                adv_score = max(adv_score, 1.0 / (1 + d1))

        # Primary: minimize target distance; Secondary: maximize opponent distance and slight center bias.
        cb = -((nx - cx) ** 2 + (ny - cy) ** 2)
        score = (-tdist) + 0.06 * opp_d + 0.08 * adv_score + center_bias * cb

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    return [int(dx), int(dy)]