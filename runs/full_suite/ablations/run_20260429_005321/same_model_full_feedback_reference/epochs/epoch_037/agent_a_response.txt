def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # If no resources, drift to center while avoiding opponent
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty) * -1 + cheb(nx, ny, ox, oy)
            if v > best_val or (v == best_val and (dx, dy) < best_move):
                best_val = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Contest resources we can reach no later than opponent; otherwise prioritize closest reachable.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        opp_safety = cheb(nx, ny, ox, oy)  # want to be farther
        best_target_score = -10**18
        for rx, ry in resources:
            t_us = cheb(nx, ny, rx, ry)
            t_op = cheb(ox, oy, rx, ry)
            if t_us <= t_op:
                # strong incentive to secure/contest; prefer lower t_us and higher margin
                margin = t_op - t_us
                score = 1000 - 10 * t_us + 20 * margin
            else:
                # if we can't beat them, move toward the closest that may become available
                score = 200 - 10 * t_us - 5 * (t_us - t_op)
            if score > best_target_score:
                best_target_score = score
        # small tie-break toward reducing overall distance to nearest resource
        nearest = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        v = best_target_score + 2 * opp_safety - 0.5 * nearest
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]