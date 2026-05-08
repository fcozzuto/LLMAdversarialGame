def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role") or "pursuer"

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    candidates = []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            candidates.append((nx, ny))

    if not candidates:
        return [0, 0]

    # Evader: maximize distance, but prefer moving toward the farthest corner from pursuer.
    # Pursuer: minimize distance.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))  # farthest from opponent
    tx, ty = best_corner if role == "evader" else (ox, oy)

    def score(nx, ny):
        if role == "evader":
            # Strongly avoid getting closer to pursuer; mildly head to corner.
            return (dist2(nx, ny, ox, oy) * 1000) - dist2(nx, ny, tx, ty)
        else:
            # Strongly approach opponent; secondarily reduce distance to same target.
            return (-dist2(nx, ny, ox, oy) * 1000) - dist2(nx, ny, tx, ty)

    best = candidates[0]
    best_s = score(best[0], best[1])
    for nx, ny in candidates[1:]:
        s = score(nx, ny)
        if s > best_s:
            best_s = s
            best = (nx, ny)

    dx, dy = best[0] - sx, best[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]