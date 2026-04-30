def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx != 0 else 0

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= grid_w or ny >= grid_h:
            return False
        return (nx, ny) not in obstacles

    # Choose target resource: prefer where we are relatively closer than opponent
    if resources:
        best = None
        best_val = None
        for rx, ry in resources:
            dm = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            val = dm - do  # smaller is better (we are closer)
            if best_val is None or val < best_val or (val == best_val and dm < best[0]):
                best_val = val
                best = (dm, rx, ry)
        target_x, target_y = best[1], best[2]
    else:
        # No resources: drift toward opponent to contest space deterministically
        target_x, target_y = ox, oy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = dist(nx, ny, target_x, target_y)
        d_from_opp = dist(nx, ny, ox, oy)
        # Score: prioritize reducing distance to target; then increase separation from opponent
        score = (d_to_target, -d_from_opp, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]