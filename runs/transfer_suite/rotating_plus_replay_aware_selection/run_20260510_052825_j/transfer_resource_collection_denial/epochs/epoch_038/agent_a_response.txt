def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obstacles:
            valid.append((rx, ry))

    if not valid:
        return [0, 0]

    tr = int(observation.get("turns_remaining", 0))
    rem = int(observation.get("remaining_resource_count", len(valid)) or len(valid))

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    fast_end = (tr <= 8) or (rem <= 3)
    best = None
    best_key = None
    prefer_even = (tr % 2 == 0)

    for rx, ry in valid:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        margin = opp_d - self_d  # +: we arrive sooner
        opp_far = opp_d
        if fast_end:
            key = (-self_d, margin, opp_far)
        else:
            # alternate between "secure closest" and "deny opponent"
            if prefer_even:
                key = (margin, opp_far, -self_d)
            else:
                key = (margin, -self_d, -opp_far)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target_sign_dx = 0 if tx == sx else (1 if tx > sx else -1)
    target_sign_dy = 0 if ty == sy else (1 if ty > sy else -1)
    wanted = [(target_sign_dx, target_sign_dy), (target_sign_dx, 0), (0, target_sign_dy), (-target_sign_dx, target_sign_dy), (0, 0)]
    cand = []
    for dx, dy in wanted + dirs:
        if (dx, dy) not in cand:
            cand.append((dx, dy))
    best_step = (0, 0)
    best_dist = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        if best_dist is None or d < best_dist:
            best_dist = d
            best_step = (dx, dy)
        if d == 0:
            break
    return [int(best_step[0]), int(best_step[1])]