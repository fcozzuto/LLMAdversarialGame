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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose a resource where we are earlier than opponent; otherwise delay opponent by picking the most "contested"
    best = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Lower is better:
        # 1) advantage = d_me - d_op (more negative means we get there first)
        # 2) our distance (shorter first)
        # 3) deterministic tie-break by coordinates
        key = (d_me - d_op, d_me, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    rx, ry = best[1]

    # Move one step toward the chosen target while keeping moves valid and (secondarily) steering to worsen opponent access.
    opp_target = None
    opp_adv = None
    for r2 in resources:
        d_me2 = cheb(sx, sy, r2[0], r2[1])
        d_op2 = cheb(ox, oy, r2[0], r2[1])
        key2 = (d_me2 - d_op2, d_me2, r2[0], r2[1])
        if opp_adv is None or key2 < opp_adv:
            opp_adv = key2
            opp_target = r2

    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_me = cheb(nx, ny, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # primary: keep improving advantage to chosen target
        # secondary: if multiple, also try to not help opponent with their best target
        d_op_help = cheb(nx, ny, opp_target[0], opp_target[1]) if opp_target else 0
        key = (d_me - d_op, d_me, d_op_help, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        # all moves blocked; stay
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]