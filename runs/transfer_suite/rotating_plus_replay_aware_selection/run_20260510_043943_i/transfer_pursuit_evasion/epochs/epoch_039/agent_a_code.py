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
            obstacles.add((int(p[0]), int(p[1])))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        dx = dx if dx >= 0 else -dx
        dy = dy if dy >= 0 else -dy
        return dx if dx >= dy else dy

    # Deterministic tie-break: fixed move order, and secondary score terms
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        # small preference to keep moving (avoid always standing still when tied)
        move_cost = (0 if (dx == 0 and dy == 0) else 1)

        # For evader: maximize distance. For pursuer: minimize distance.
        # Also discourage positions adjacent to obstacles (soft safety for evader, soft wall-hugging for pursuer).
        adj_obs = 0
        for ax, ay in moves:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                adj_obs += 1

        if is_evader:
            score = (d * d) + (0.15 * move_cost) - (0.02 * adj_obs)
            better = (best_score is None) or (score > best_score)
        else:
            score = (-(d * d)) + (0.15 * move_cost) - (0.02 * adj_obs)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_move = [dx, dy]

    return best_move