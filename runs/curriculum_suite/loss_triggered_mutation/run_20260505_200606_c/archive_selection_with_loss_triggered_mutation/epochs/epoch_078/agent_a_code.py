def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def best_next_pos(px, py, target):
        tx, ty = target
        best = None; bestv = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not legal(nx, ny): 
                continue
            # prefer reducing distance to target; tie-break by closer to our current center
            v = man(nx, ny, tx, ty)
            if best is None or v < bestv or (v == bestv and (nx, ny) < best):
                best, bestv = (nx, ny), v
        return best if best is not None else (px, py)

    def score_move_for_resource(rx, ry, mx, my):
        # Two-ply: we move, opponent replies greedily toward same resource.
        nx, ny = mx, my
        ox2, oy2 = best_next_pos(ox, oy, (rx, ry))
        d_me = man(nx, ny, rx, ry)
        d_op = man(ox2, oy2, rx, ry)
        # Prefer resources we can reach much sooner; slight tie-break on remaining distance.
        return (d_op - d_me) * 10 - (d_me + 0.3 * d_op)

    if not resources:
        # Deterministic drift: go toward the corner opposite opponent (block-sweep friendly).
        goal = (0, 7) if ox > w // 2 else (7, 0)
        gx, gy = goal
        best = (0, 0); bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = man(nx, ny, gx, gy)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                best, bestv = (dx, dy), v
        return [best[0], best[1]]

    # Choose our move that maximizes the best achievable resource advantage after opponent reply.
    best_move = (0, 0); best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # evaluate top resource only (fast) with deterministic selection
        best_r_val = None
        # Prefer resources that are likely contested: min(d_me) and also (d_op - d_me)
        # Deterministic ordering to avoid ties.
        for rx, ry in sorted(resources):
            base = man(sx, sy, rx, ry) - 0.9 * man(ox, oy, rx, ry)
            # prune lightly: consider near ones first by base
            if best_r_val is not None and base > 50 and best_r_val < -10:
                continue
            v = score_move_for_resource(rx, ry, nx, ny)
            if best_r_val is None or v > best_r_val:
                best_r_val = v
        if best_val is None or best_r_val > best_val or (best_r_val == best_val and (dx, dy) < best_move):
            best_val = best_r_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]