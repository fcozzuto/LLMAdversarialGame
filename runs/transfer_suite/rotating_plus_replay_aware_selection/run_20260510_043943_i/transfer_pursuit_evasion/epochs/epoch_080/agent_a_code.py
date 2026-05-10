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

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    if is_evader:
        best_val = -10**9
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            dist_to_opp = cheb(nx, ny, ox, oy)
            dist_to_corner = cheb(nx, ny, far_corner[0], far_corner[1])
            dist_to_other = cheb(nx, ny, near_corner[0], near_corner[1])
            # Prefer increasing distance; secondarily go to far corner; avoid giving up ground.
            val = 100 * dist_to_opp + 3 * dist_to_corner - 2 * dist_to_other
            # Mild preference for staying off the "line" toward opponent.
            val -= (abs((ox - nx)) + abs((oy - ny))) * 0.01
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        best_val = -10**9
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            dist_to_opp = cheb(nx, ny, ox, oy)
            # Prefer minimizing distance; slight bias to cut diagonally.
            val = -100 * dist_to_opp - (abs(dx) + abs(dy)) * 0.01
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]