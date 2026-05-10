def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    def valid(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return False
        return (nx, ny) not in obstacles

    def obstacle_pressure(nx, ny):
        # Prefer not to walk into/near obstacles deterministically.
        best = 99
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    if is_evader:
        best_score = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_op = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, target_corner[0], target_corner[1])
            # Maximize distance from pursuer; also keep progressing to corner; avoid obstacles.
            score = (d_op * 100) + (d_corner) + (obstacle_pressure(nx, ny) * 2)
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
    else:
        best_score = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_op = cheb(nx, ny, ox, oy)
            # Pursue while cutting off opponent access to corners.
            d_corner = cheb(nx, ny, target_corner[0], target_corner[1])
            score = (d_op * 100) - d_corner - (obstacle_pressure(nx, ny))
            if score < best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]