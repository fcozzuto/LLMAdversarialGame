def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evade" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in moves if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Bias for corner-seeking evasion / corner-denying pursuit
    far_corner = max(corners, key=lambda c: md(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: md(c[0], c[1], ox, oy))

    best_move = None
    if is_evader:
        # Prefer moves that increase distance; if tied, move toward far_corner.
        best_score = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dist = md(nx, ny, ox, oy)
            corner_dist = md(nx, ny, far_corner[0], far_corner[1])
            score = (dist, -corner_dist, -abs(nx - far_corner[0]) - abs(ny - far_corner[1]))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # Pursuer: try to capture; otherwise reduce distance and "cut off" by pushing toward near_corner.
        best_score = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dist = md(nx, ny, ox, oy)
            corner_dist = md(nx, ny, near_corner[0], near_corner[1])
            capture = 1 if (nx == ox and ny == oy) else 0
            score = (capture, -dist, -corner_dist)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]