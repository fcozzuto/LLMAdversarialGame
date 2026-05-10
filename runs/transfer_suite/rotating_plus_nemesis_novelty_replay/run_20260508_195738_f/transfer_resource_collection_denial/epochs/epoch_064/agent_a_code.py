def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        resources.append((int(r[0]), int(r[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_move_towards(tx, ty, prefer_from_opponent=False):
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            key = (d_self, d_opp if prefer_from_opponent else -d_opp, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    remaining = observation.get("remaining_resource_count", None)
    if remaining is not None and int(remaining) <= 0:
        return best_move_towards(ox, oy, prefer_from_opponent=False)

    if resources:
        best_target = None
        for rx, ry in resources:
            key = (cheb(sx, sy, rx, ry), rx, ry)
            if best_target is None or key < best_target[0]:
                best_target = (key, (rx, ry))
        tx, ty = best_target[1]
        return best_move_towards(tx, ty, prefer_from_opponent=True)

    return best_move_towards(ox, oy, prefer_from_opponent=False)