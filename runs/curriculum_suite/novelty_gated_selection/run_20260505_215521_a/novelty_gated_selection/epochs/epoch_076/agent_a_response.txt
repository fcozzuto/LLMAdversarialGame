def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def eval_from(px, py):
        best = (-10**9, 10**9, 10**9)
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer; strongly deny opponent when possible
            rel = od - sd
            if (rel, -sd, od) > best:
                best = (rel, -sd, od)
        # If no resources, simply move away from opponent while staying safe
        if not resources:
            return (-cheb(px, py, ox, oy), 0, 0)
        return best

    # Prefer a move that maximizes the best resource we can "claim first"
    best_move = (0, 0)
    best_score = (-10**9, -10**9, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            sc = eval_from(nx, ny)
            if sc > best_score:
                best_score = sc
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]