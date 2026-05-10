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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = [0, 0]
    best_val = None

    # Small deterministic bias to break ties toward moving "outward" from start-corners.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    start_corner = max(corners, key=lambda c: cheb(c[0], c[1], sx, sy))
    scx, scy = start_corner

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        # Penalty for moving next to obstacles (counts Chebyshev adjacency)
        adj = 0
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) <= 1:
                adj += 1
        # Preference for staying away from the start corner if evading (deterministic)
        corner_bias = -cheb(nx, ny, scx, scy) if is_evader else cheb(nx, ny, scx, scy)
        if is_evader:
            val = dist * 10.0 + corner_bias - adj * 0.5
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            val = -dist * 10.0 + corner_bias - adj * 0.5
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]