def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    mode_evader = "evader" in self_role

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    goalx, goaly = far_corner if mode_evader else near_corner

    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                cnt += 1
        return cnt

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d2 = dist2(nx, ny, ox, oy)
        corner_d2 = dist2(nx, ny, goalx, goaly)
        neigh = free_neighbors(nx, ny)

        if mode_evader:
            # maximize distance from pursuer; prefer toward farthest corner; avoid tight cells
            score = d2 * 4.0 - corner_d2 * 0.35 + neigh * 0.15
        else:
            # minimize distance to evader; prefer toward near corner to constrain; avoid tight cells
            score = -d2 * 4.0 - corner_d2 * 0.15 + neigh * 0.10

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move