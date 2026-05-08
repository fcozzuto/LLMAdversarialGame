def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # Pick a target that we can reach before the opponent (or at least threaten)
    best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        lead = op_d - my_d  # positive => we are ahead
        # Secondary: prefer closer targets and avoid wasting time on "already too far behind" ones
        key = (-lead, my_d, op_d, rx, ry)  # we choose most favorable lead by minimizing -lead
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # If opponent is significantly closer to their nearest resource, switch to contest it
    # (deterministic "interceptor" twist: compute opponent nearest and our best response)
    op_nearest = None
    op_best_d = None
    for rx, ry in resources:
        d = dist8(ox, oy, rx, ry)
        if op_best_d is None or d < op_best_d or (d == op_best_d and (rx, ry) < op_nearest):
            op_best_d = d
            op_nearest = (rx, ry)
    if op_nearest is not None:
        my_to_op = dist8(sx, sy, op_nearest[0], op_nearest[1])
        op_to_op = op_best_d
        if op_to_op - my_to_op >= 2:
            # Contest opponent-nearest if we can plausibly deny it next step
            tx, ty = op_nearest

    cur_my_d = dist8(sx, sy, tx, ty)
    cur_op_d = dist8(ox, oy, tx, ty)

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        # Score: maximize our improvement and deny opponent's progress
        my_improve = cur_my_d - nd
        op_d = cur_op_d  # opponent doesn't move this turn, but we can still deny by closeness
        my_close = -nd
        opp_adv = op_d - nd  # how far ahead we are after moving toward target
        # Small obstacle-avoidance proxy: prefer moves farther from obstacles (deterministic)
        near_obst = 0
        for ox2, oy2 in obst:
            d = abs(nx - ox2)
            e = abs(ny - oy2)
            dd = d if d > e else e
            if dd <= 1:
                near_obst += 1
        score = (opp_adv, my_improve, my_close, -near_obst, nx, ny, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move