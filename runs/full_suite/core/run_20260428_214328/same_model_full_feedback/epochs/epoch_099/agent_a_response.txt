def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    # Evaluate a move by best attainable "advantage" over opponent for some resource,
    # plus a small term that discourages giving the opponent an immediate easy steal.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Immediate steal threat to opponent if we move away:
        opp_threat = 0
        for rx, ry in resources:
            d_op_next = cheb(ox, oy, rx, ry)
            if d_op_next == 1:
                opp_threat += 2
            elif d_op_next == 2:
                opp_threat += 1

        # Choose resource maximizing our advantage (op - me); tie-break by closer-to-me.
        best_adv = None
        best_res_d = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_me  # positive means we can reach strictly sooner (or at least not later)
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_res_d is None or d_me < best_res_d)):
                best_adv = adv
                best_res_d = d_me

        # Prefer making/keeping advantage, and if tied, prefer reducing our distance to the target.
        score = best_adv * 10 - (best_res_d or 0) - opp_threat
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]