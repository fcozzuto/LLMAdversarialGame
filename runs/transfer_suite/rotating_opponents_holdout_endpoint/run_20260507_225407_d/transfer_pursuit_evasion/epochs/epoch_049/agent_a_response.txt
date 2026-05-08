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
    mode = "evade" if "evader" in self_role else "pursue"

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    # Determine target corners deterministically for evader
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myd = dist2(nx, ny, ox, oy)
        if mode == "evade":
            # Maximize distance to pursuer; also head toward the farthest corner from pursuer
            corner_bias = dist2(nx, ny, far_corner[0], far_corner[1])
            # Prefer corner if already close to it: minimize remaining distance to that corner
            corner_bias = -dist2(nx, ny, far_corner[0], far_corner[1])
            score = (myd * 10) + corner_bias
        else:
            # Minimize distance to evader; also slightly bias toward the corner closer to evader
            corner_bias = dist2(nx, ny, near_corner[0], near_corner[1])
            score = (-myd * 10) - (corner_bias * 0.01)

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]