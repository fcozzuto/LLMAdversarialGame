def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 1 or h < 1 or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    nearest_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    farthest_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    tx = (ox + farthest_corner[0]) // 2
    ty = (oy + farthest_corner[1]) // 2

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def obstacle_pen(x, y):
        if not obstacles:
            return 0.0
        best = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best == 0:
            return 1e6
        return 3.0 / best

    # Move toward an "intercept" target, but bias away from heading directly into the evader's escape corner.
    best_score = -1e18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_op = abs(nx - ox) + abs(ny - oy)
        d_to_target = abs(nx - tx) + abs(ny - ty)
        d_op_to_corner = abs(ox - farthest_corner[0]) + abs(oy - farthest_corner[1])
        d_nx_to_corner = abs(nx - farthest_corner[0]) + abs(ny - farthest_corner[1])
        # Prefer reducing distance to opponent, and to intercept target, while not getting closer to the opponent's farthest corner too much.
        score = (-1.7 * d_to_op) + (-0.9 * d_to_target) + (0.35 * (d_nx_to_corner - d_op_to_corner)) - obstacle_pen(nx, ny)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move