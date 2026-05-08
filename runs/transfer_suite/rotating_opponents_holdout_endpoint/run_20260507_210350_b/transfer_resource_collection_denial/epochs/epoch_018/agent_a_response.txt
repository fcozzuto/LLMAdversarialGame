def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def resource_value(px, py, tx, ty):
        sd = man(px, py, tx, ty)
        od = man(ox, oy, tx, ty)
        margin = od - sd  # positive => we are closer
        # deterministic tie-breaker to avoid oscillation
        tie = (tx * 113 + ty * 59 + sd * 7 + od * 3) % 1000
        # Encourage immediate pickup; otherwise contest control
        pickup = 50 if (px == tx and py == ty) else 0
        return pickup + margin * 10 - sd + (tie * 0.0001)

    best_move = (0, 0)
    best_score = -10**18

    # Choose move that maximizes our best contested resource advantage after the move.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # compute our best resource post-move
        top = -10**18
        for tx, ty in resources:
            v = resource_value(nx, ny, tx, ty)
            if v > top:
                top = v
        # intercept bias: if opponent is much closer to some resource, reduce that distance.
        # (choose nearest resource to opponent as secondary pressure)
        opp_near = None
        opp_best = 10**9
        for tx, ty in resources:
            d = man(ox, oy, tx, ty)
            if d < opp_best:
                opp_best = d
                opp_near = (tx, ty)
        if opp_near is not None:
            tx, ty = opp_near
            opp_margin = man(nx, ny, tx, ty) - man(ox, oy, tx, ty)  # negative => we catch up
            # prioritize catch-up only when opponent is ahead
            if man(ox, oy, tx, ty) + 1 < man(sx, sy, tx, ty):
                top += (-opp_margin) * 2
        # small deterministic penalty for staying still to prevent loops (unless already best)
        stay_pen = 0.2 if (dx == 0 and dy == 0) else 0.0
        score = top - stay_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not valid(sx + dx, sy + dy):
        return [0, 0]
    return [int(dx), int(dy)]