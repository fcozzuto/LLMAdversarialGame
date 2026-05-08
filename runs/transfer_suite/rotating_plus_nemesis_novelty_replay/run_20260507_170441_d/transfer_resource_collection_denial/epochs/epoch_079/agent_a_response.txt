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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        # simple fallback: stay safe from opponent
        best = (dist8(sx, sy, ox, oy), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d = dist8(nx, ny, ox, oy)
                if d > best[0]:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    # Choose best target resource based on who can reach it first (chebyshev time).
    best_target = resources[0]
    best_key = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        # Prefer resources we can beat; then closer.
        key = (-(op_d - my_d), my_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)
    tx, ty = best_target

    # If opponent is already on/near this resource, consider a safer alternative deterministically.
    if dist8(ox, oy, tx, ty) <= 1 and len(resources) > 1:
        alt_key = None
        alt = best_target
        for rx, ry in resources:
            if (rx, ry) == best_target:
                continue
            my_d = dist8(sx, sy, rx, ry)
            op_d = dist8(ox, oy, rx, ry)
            key = (-(op_d - my_d), my_d, rx, ry)
            if alt_key is None or key < alt_key:
                alt_key = key
                alt = (rx, ry)
        tx, ty = alt

    # Evaluate moves: maximize advantage on chosen target, plus avoid getting too close to opponent.
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        my_adv = dist8(ox, oy, tx, ty) - nd  # higher is better
        opp_contact_pen = 0
        do = dist8(nx, ny, ox, oy)
        if do <= 1:
            opp_contact_pen = 6
        if do == 0:
            opp_contact_pen = 10
        # Small bias toward reducing distance to target.
        score = (my_adv * 10) - opp_contact_pen - nd
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]