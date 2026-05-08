def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None:
            obst.add((p[0], p[1]))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def md(a, b, x, y):
        return max(abs(x - a), abs(y - b))

    if not resources:
        return [0, 0]

    r_best = None
    my_d = None
    op_d = None
    for rx, ry in resources:
        d1 = md(rx, ry, sx, sy)
        d2 = md(rx, ry, ox, oy)
        if r_best is None or (d1, d2) < (my_d, op_d):
            r_best = (rx, ry)
            my_d, op_d = d1, d2

    rx, ry = r_best
    opp_has_edge = (op_d is not None and my_d is not None and op_d < my_d)

    best = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = md(rx, ry, nx, ny)
        # Encourage collecting the target; if opponent is closer, also steer to reduce their advantage.
        d_opp = md(rx, ry, ox, oy)
        adv = d_opp - d_self  # positive if we are closer than opponent
        score = (-d_self)
        score += (0.35 * adv) if opp_has_edge else (0.18 * (-d_self))
        # Light tie-break: avoid idling; slightly prefer moves that bring us closer to center if same distance.
        if dx == 0 and dy == 0:
            score -= 0.15
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= 0.001 * (md(int(cx), int(cy), nx, ny))
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]