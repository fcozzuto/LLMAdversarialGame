def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    legal = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]
    if not legal or not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def dist(p, q):
        return man(p[0], p[1], q[0], q[1])

    def next_step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy):
            return (dx, dy)
        best = None
        bestv = 10**18
        for ddx, ddy in legal:
            nx, ny = sx + ddx, sy + ddy
            v = man(nx, ny, tx, ty)
            if v < bestv:
                bestv = v
                best = (ddx, ddy)
        return best if best is not None else (0, 0)

    # Predict opponent's likely target: closest resource to them.
    opp_target = min(resources, key=lambda r: (dist((ox, oy), r), r[0], r[1]))
    my_to_opp_target = dist((sx, sy), opp_target)
    opp_to_opp_target = dist((ox, oy), opp_target)

    # If we can reach (or tie) their likely target, contest it directly.
    if my_to_opp_target <= opp_to_opp_target:
        return list(next_step_toward(opp_target[0], opp_target[1]))

    # Otherwise, deny by selecting a resource that maximizes our lead over the opponent.
    # Secondary objective: increase separation from opponent if leads are similar.
    def cell_score(r):
        myd = dist((sx, sy), r)
        opd = dist((ox, oy), r)
        sep = man(sx, sy, ox, oy)
        lead = opd - myd
        return (lead, sep - myd, -myd)

    target = max(resources, key=cell_score)
    return list(next_step_toward(target[0], target[1]))