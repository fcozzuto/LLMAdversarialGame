def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    resources = observation.get("resources", None)
    use_resource = observation.get("remaining_resource_count", 0)
    if isinstance(use_resource, (int, float)) and use_resource > 0 and resources:
        best = None
        for r in resources:
            try:
                rx, ry = r[0], r[1]
            except Exception:
                continue
            if valid(rx, ry):
                v = dist2(sx, sy, rx, ry)
                if best is None or v < best[0]:
                    best = (v, rx, ry)
        tx, ty = (best[1], best[2]) if best else (ox, oy)
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = dist2(nx, ny, tx, ty)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if valid(sx, sy):
        return [int(best_move[0]), int(best_move[1])]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]