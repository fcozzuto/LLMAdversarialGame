def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opponent_role and "pursuer" in self_role is False)
    is_pursuer = not is_evader

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sq(a, b): return a*a + b*b

    # Predict evader step direction as continuing away from pursuer.
    vx, vy = ox - sx, oy - sy
    step_dx = 0 if vx == 0 else (1 if vx > 0 else -1)
    step_dy = 0 if vy == 0 else (1 if vy > 0 else -1)
    tx, ty = ox + step_dx, oy + step_dy
    if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
        tx, ty = ox, oy

    # Evader target: maximize distance + prefer keeping a "wall-running" bias (hug a boundary).
    # Pursuer target: minimize distance to predicted target, with small tie-break for cutting off escape.
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if is_pursuer:
            d_to_target = sq(nx - tx, ny - ty)
            # Escape-cut tie-break: prefer moves that reduce ability to increase distance along dx/dy away direction.
            # Compute angle-aligned improvement: next opponent-away vector from pursuer.
            ev_dir_x = step_dx
            ev_dir_y = step_dy
            # Prefer being closer along evader direction line: project vector from opponent to pursuer onto evader-away.
            proj = (sx - ox) * ev_dir_x + (sy - oy) * ev_dir_y
            # Slightly penalize positions far from current opponent to avoid overshooting through obstacles.
            d_to_op = sq(nx - ox, ny - oy)
            score = (d_to_target, d_to_op, proj)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        else:
            d = sq(nx - ox, ny - oy)
            # Wall-run bias: prefer closer to a boundary that keeps opponent blocked.
            dist_left = nx
            dist_right = (w - 1) - nx
            dist_up = ny
            dist_down = (h - 1) - ny
            boundary_bias = min(dist_left, dist_right, dist_up, dist_down)
            # Prefer not to step into adjacency with opponent.
            adj_pen = 0 if max(abs(nx - ox), abs(ny - oy)) > 1 else -1000
            # Prefer continuing away (same sign as away direction).
            away_bonus = (nx - sx) * (sx - ox) + (ny - sy) * (sy - oy)
            score = (d, -boundary_bias, adj_pen + away_bonus)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]