def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obstacle_penalty(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    pen += 1
        return pen

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty) - 2 * near_obstacle_penalty(nx, ny)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Evaluate move by best achievable resource advantage, with a small contest term.
        move_best = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Strongly prefer resources we can reach sooner; if we can't, still try to deny by contesting.
            val = (d_op - d_me) * 8 - d_me + (1 if d_me == d_op else 0) - 2 * near_obstacle_penalty(nx, ny)
            if val > move_best:
                move_best = val
        # Tie-breakers: prefer reducing distance to currently most "threatening" resource.
        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)
        elif move_best == best_score:
            cur_tgt = resources[0]
            # Deterministic secondary: prefer staying if equal distance, else smaller dx/dy lexicographically.
            # Compute a compact tie metric to avoid randomness.
            t_best = (cheb(sx, sy, cur_tgt[0], cur_tgt[1]), dx, dy)
            t_new = (cheb(nx, ny, cur_tgt[0], cur_tgt[1]), best_move[0], best_move[1])
            if t_best < t_new:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]