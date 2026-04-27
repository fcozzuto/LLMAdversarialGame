def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick best target: maximize advantage for us (closer than opponent), break ties deterministically.
    best_t = None
    best_adv = -10**9
    for rx, ry in resources:
        dme = cheb((mx, my), (rx, ry))
        dpp = cheb((ox, oy), (rx, ry))
        adv = dpp - dme  # positive means we are closer
        # slight preference for nearer resources when advantages tie
        key = (adv, -(dme + dpp), -((rx + 1) * 100 + (ry + 1)))
        if (adv > best_adv) or (adv == best_adv and best_t is None) or (best_t is not None and key > (0, 0, 0)):
            best_adv = adv
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    # Evaluate moves by resulting advantage + progress; also avoid stepping away when opponent is close.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        my_d = cheb((nx, ny), (tx, ty))
        op_d = cheb((ox, oy), (tx, ty))
        cur_d = cheb((mx, my), (tx, ty))
        prog = cur_d - my_d  # positive if we move closer
        # pressure term: if opponent is within 1 move, prioritize reducing our distance heavily
        pressure = 5 if op_d <= 1 else 0
        val = (op_d - my_d) * 10 + prog * 3 + pressure * (cur_d - my_d)
        # deterministic tie-break: prefer smaller dx then dy then stay
        tie = (val == best_val and (abs(dx) < abs(best_move[0]) or (abs(dx) == abs(best_move[0]) and (dy < best_move[1]))))
        if val > best_val or tie:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]