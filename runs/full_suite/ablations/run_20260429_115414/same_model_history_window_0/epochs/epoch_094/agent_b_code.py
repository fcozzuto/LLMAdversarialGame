def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    me = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(xy) for xy in observation.get("obstacles", []))

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    mx, my = me
    ox, oy = op
    res = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not res:
        # No resources: drift toward center while avoiding obstacles
        target = (w // 2, h // 2)
    else:
        best = None
        best_score = None
        for r in res:
            d_me = cheb(me, r)
            d_op = cheb(op, r)
            score = d_op - d_me  # higher means I'm relatively closer
            if best_score is None or score > best_score or (score == best_score and d_me < cheb(me, best)):
                best_score = score
                best = r
        # If I'm not clearly closer to any, just take the closest resource
        if best_score is not None and best_score < 0:
            best = min(res, key=lambda r: cheb(me, r))
        target = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (target[0], target[1]):
            val = 10**9  # prioritize immediate capture
        else:
            d_t = cheb((nx, ny), target)
            d_o = cheb((nx, ny), (ox, oy))
            val = -d_t + 0.01 * d_o  # slight preference to stay away from opponent
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move if best_val is not None else [0, 0]