def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx = 0 if sx > w - 1 - sx else w - 1
        ty = 0 if sy > h - 1 - sy else h - 1
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                d = cheb(nx, ny, tx, ty)
                cand = (d, nx, ny)
                if best is None or cand < best:
                    best = cand
        return [best[1] - sx, best[2] - sy] if best else [0, 0]

    # Choose a target that favors winning the race (your distance minus opponent distance)
    # Use a stronger weight on opponent distance shift to change behavior vs prior epochs.
    def target_value(r):
        rx, ry = r
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        return (ds - 1.35 * do, ds + do, rx, ry)

    targets_sorted = sorted(resources, key=target_value)
    # Consider top few targets deterministically
    candidates = targets_sorted[:min(4, len(targets_sorted))]

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Evaluate move by improvement toward the best target(s) and increasing opponent's distance to it.
        score = None
        for (rx, ry) in candidates:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            cur_my_d = cheb(sx, sy, rx, ry)
            # Prefer reducing own distance, and if possible, widen the race gap.
            val = (my_d - 1.65 * op_d, my_d, (cur_my_d - my_d), -op_d, rx, ry)
            if score is None or val < score:
                score = val
        # Tie-break deterministically toward moves that keep away from opponent
        away = cheb(nx, ny, ox, oy)
        cand = (score[0], -away, nx, ny, dx, dy)
        if best_move is None or cand < best_move:
            best_move = cand

    if best_move is None:
        return [0, 0]
    return [best_move[4], best_move[5]]