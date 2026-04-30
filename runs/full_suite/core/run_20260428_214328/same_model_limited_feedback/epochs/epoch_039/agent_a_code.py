def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    my = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cx, cy = int(my[0]), int(my[1])
    ox, oy = int(op[0]), int(op[1])

    def d2(a, b):  # squared distance, diagonal-friendly
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Pick a target resource where we are relatively closer than the opponent.
    best_t = None
    best_pr = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        myd = d2((cx, cy), (rx, ry))
        opd = d2((ox, oy), (rx, ry))
        pr = (opd - myd) - 0.01 * myd  # prefer resources opponent can't easily claim
        if best_pr is None or pr > best_pr:
            best_pr = pr
            best_t = (rx, ry)

    if best_t is None:
        # No resources: maximize distance from opponent while avoiding obstacles
        target = (ox, oy)
    else:
        target = best_t

    tx, ty = target

    # Decide movement: greedy toward target, but if contested (we're far), prioritize spacing.
    contested = 0
    if best_pr is not None and best_pr < -1e-9:
        contested = 1

    best_mv = [0, 0]
    best_sc = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = cx + dx, cy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            dist_t = d2((nx, ny), (tx, ty))
            dist_op = d2((nx, ny), (ox, oy))
            sc = -dist_t
            sc += (0.35 if contested else 0.12) * dist_op
            # Slight preference to not move into "dead" proximity to opponent when contested
            if contested:
                sc += -0.08 * (dist_op == 0)
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]