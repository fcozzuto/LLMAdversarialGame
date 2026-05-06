def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    # Prefer moves that increase (opponent_distance - self_distance) to the best contested resource.
    # Small tie-breakers: prefer closer self, then fewer obstacle-adjacent directions (more stability).
    def obstacle_adjacency(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    best = None  # (score_tuple, dx, dy)
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        best_res_score = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Score components: larger is better for first two, smaller for last.
            score = (od - sd, -sd, -abs(rx - nx) - abs(ry - ny), obstacle_adjacency(nx, ny))
            if best_res_score is None or score > best_res_score:
                best_res_score = score
        if best_res_score is None:
            continue
        if best is None or best_res_score > best[0]:
            best = (best_res_score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]