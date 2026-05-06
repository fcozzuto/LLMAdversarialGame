def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)
    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_target = None
    opp_td = 10**9
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < opp_td:
            opp_td = d
            opp_target = (rx, ry)

    my_near = None
    my_nd = 10**9
    for rx, ry in resources:
        d = man(sx, sy, rx, ry)
        if d < my_nd:
            my_nd = d
            my_near = (rx, ry)

    tx, ty = opp_target if opp_target is not None else my_near
    if tx is None:
        return [0, 0]

    my_to_opp_t = man(sx, sy, tx, ty)
    my_plan_target = (tx, ty) if my_to_opp_t <= opp_td else my_near

    best_dx, best_dy = 0, 0
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_my = man(nx, ny, my_plan_target[0], my_plan_target[1])
        d_opp = man(nx, ny, ox, oy)

        # Resource contest: advantage over opponent's current best (opponent target)
        d_opp_to_target = man(ox, oy, my_plan_target[0], my_plan_target[1])
        adv = (d_opp_to_target - d_my)

        # If we are not the intended chaser, slightly prefer moving toward our nearest.
        alt_adv = 0.0
        if my_plan_target != my_near:
            alt_adv = man(ox, oy, my_near[0], my_near[1]) - man(nx, ny, my_near[0], my_near[1])

        # Obstacle sensitivity: penalize stepping next to obstacles to reduce getting stuck.
        adj_obs = 0
        for ddx, ddy in deltas:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in obstacles:
                adj_obs += 1

        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.02
        score = 2.2 * adv + 0.7 * alt_adv - 0.35 * adj_obs + 0.06 * center - 0.01 * d_opp

        if score > best_score or (score == best_score and (dx, dy) < (best_dx, best_dy)):
            best_score, best_dx, best_dy = score, dx, dy

    return [int(best_dx), int(best_dy)]