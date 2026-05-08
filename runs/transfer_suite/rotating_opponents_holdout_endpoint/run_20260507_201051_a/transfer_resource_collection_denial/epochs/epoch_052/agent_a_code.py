def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy  # Chebyshev

    best_r = resources[0]
    best_key = None
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        # Prefer higher reach advantage; then closer; then deterministic spatial tie-break
        key = (od - sd, -sd, -(abs(r[0]) + abs(r[1])), -(r[0] * 16 + r[1]))
        if best_key is None or key > best_key:
            best_key, best_r = key, r

    tx, ty = best_r
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        # Also avoid moving too close to opponent if it doesn't help
        ao = dist((nx, ny), (ox, oy))
        score = (-nd, -ao, -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)))
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]