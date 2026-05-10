def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    self_role = observation.get("self_role", "pursuer")
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2 and isinstance(p[0], int) and isinstance(p[1], int):
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if self_role == "evader":
        target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        target_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        opp_d2 = dist2(nx, ny, ox, oy)

        if self_role == "evader":
            corner_d2 = dist2(nx, ny, target_corner[0], target_corner[1])
            score = (opp_d2 * 3.0) + (corner_d2 * 0.5)
        else:
            corner_d2 = dist2(nx, ny, target_corner[0], target_corner[1])
            score = (-opp_d2 * 3.0) + (-corner_d2 * 0.15)

        # discourage stepping into "tight" spots (few available neighboring cells)
        neigh_free = 0
        for mx, my in moves:
            tx, ty = nx + mx, ny + my
            if inb(tx, ty):
                neigh_free += 1
        score += (neigh_free * (0.12 if self_role == "evader" else -0.12))

        if best_score is None or (self_role == "evader" and score > best_score) or (self_role != "evader" and score < best_score):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]