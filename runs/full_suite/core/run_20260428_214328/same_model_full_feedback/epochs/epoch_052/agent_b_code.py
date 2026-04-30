def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx if dx >= 0 else -dx if dy >= 0 else -dy

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best_score = None
    best_move = (0, 0)

    # Targets: nearest resource, then if none, push toward center and away from opponent.
    center = (w // 2, h // 2)
    res_list = resources
    prefer_opponent_side = (sx + sy) > (ox + oy)

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny):
            nx, ny = sx, sy

        # Resource pressure
        if res_list:
            my_best = min(dist2(nx, ny, rx, ry) for rx, ry in res_list)
            op_best = min(dist2(ox, oy, rx, ry) for rx, ry in res_list)
            # If we're closer to the best resource than opponent, reward.
            rel = op_best - my_best  # positive is good
            score = 20000 * (1 if rel > 0 else 0) + 30 * rel - my_best
        else:
            score = -dist2(nx, ny, center[0], center[1])

        # Safety/contesting: don't step into opponent's immediate neighborhood unless it also improves resources.
        opp_dist = dist2(nx, ny, ox, oy)
        score -= 1200 // (1 + opp_dist)

        # Deterministic tie-break via slight preference based on direction and position.
        score -= 0.001 * (nx + 3 * ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dxm, dym)
        elif score == best_score:
            # Deterministic order: smaller dx then smaller dy.
            if (dxm, dym) < best_move:
                best_move = (dxm, dym)

    # If no resources, optionally bias toward opponent side corner to contest unseen resources.
    if not resources:
        tx, ty = (w - 1, h - 1) if prefer_opponent_side else (0, 0)
        # Move one step toward tx,ty with obstacle check.
        dx_t = 0 if tx == sx else (1 if tx > sx else -1)
        dy_t = 0 if ty == sy else (1 if ty > sy else -1)
        cand = (dx_t, dy_t)
        nx, ny = sx + cand[0], sy + cand[1]
        if inside(nx, ny):
            best_move = cand

    return [int(best_move[0]), int(best_move[1])]