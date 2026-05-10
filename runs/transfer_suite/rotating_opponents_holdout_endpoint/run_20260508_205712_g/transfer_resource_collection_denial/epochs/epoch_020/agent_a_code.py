def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set(resources)

    # Choose a "best" target resource deterministically
    my_best = (10**9, None)
    op_best = (10**9, None)
    lead = []
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        if myd < my_best[0]:
            my_best = (myd, (rx, ry))
        if opd < op_best[0]:
            op_best = (opd, (rx, ry))
        lead.append((opd - myd, opd, myd, (rx, ry)))  # advantage: positive if we are closer

    # If opponent is closer to their closest resource, contest; otherwise grab best available
    deny_mode = op_best[0] < my_best[0]

    # Pick target based on mode
    target = None
    if deny_mode:
        # Contest the resource where opponent is closest, breaking ties by our relative closeness
        cand = []
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            cand.append((opd, myd, -(opd - myd), (rx, ry)))
        cand.sort()
        target = cand[0][3]
    else:
        # Pick resource with maximum advantage; break ties by smaller our distance then by coordinates
        lead.sort(key=lambda t: (-t[0], t[2], t[3][0], t[3][1]))
        target = lead[0][3]
        if target is None:
            target = my_best[1]

    tx, ty = target

    # Evaluate each move by next-step distance to target plus opponent-advantage pressure
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in res_set:
            immediate = 1000000
        else:
            immediate = 0

        myd_next = cheb(nx, ny, tx, ty)
        opd_to_tx = cheb(ox, oy, tx, ty)
        # Encourage moving closer when opponent is also threatening; otherwise just go for target
        pressure = 0
        if deny_mode:
            pressure = (opd_to_tx - myd_next) * 200
        else:
            pressure = (opd_to_tx - myd_next) * 50

        # Small bias toward reducing overall resource distance to avoid dead ends without pathfinding
        overall = 0
        for rx, ry in resources:
            overall = min(overall, cheb(nx, ny, rx, ry)) if overall != 0 else cheb(nx, ny, rx, ry)

        val = immediate - myd_next * 10 + pressure - overall * 1
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]