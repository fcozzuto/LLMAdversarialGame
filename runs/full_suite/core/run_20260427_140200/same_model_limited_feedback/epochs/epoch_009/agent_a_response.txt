def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((x, y) for x, y in obstacles)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dy == 0 else (dy if dy >= 0 else -dy) if dx == 0 else (dx if dx >= 0 else -dx if dy == 0 else (dy if dy >= 0 else -dy))

    # simpler: Chebyshev distance
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose resource that maximizes my advantage over opponent (my_dist - opp_dist minimized)
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        key = (myd - opd, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        target_x, target_y = ox, oy
    else:
        target_x, target_y = best_res

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        myd = dist(nx, ny, target_x, target_y)
        opd = dist(ox, oy, target_x, target_y)
        # Prefer moves that reduce my distance to target, and also avoid giving opponent a big lead
        lead_penalty = dist(nx, ny, ox, oy)  # closer to opponent slightly worse (deterministic tie-breaker)
        val = (myd, (myd - opd), lead_penalty, abs(dx) + abs(dy), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]