def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles") or []):
        if o is not None and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        target = min(resources, key=lambda p: (dist((sx, sy), p), p[0], p[1]))
        best_move = None
        best_d = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist((nx, ny), target)
            if d < best_d or (d == best_d and (dx, dy) < best_move):
                best_d = d
                best_move = (dx, dy)
        if best_move is not None:
            return [best_move[0], best_move[1]]
    else:
        # No visible resources: deterministically move toward opponent, preferring closer Chebyshev distance.
        best_move = None
        best_d = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist((nx, ny), (ox, oy))
            if d < best_d or (d == best_d and (dx, dy) < best_move):
                best_d = d
                best_move = (dx, dy)
        if best_move is not None:
            return [best_move[0], best_move[1]]

    return [0, 0]