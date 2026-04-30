def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obstacles = set(tuple(o) for o in obstacles)

    resources = observation.get("resources", []) or []
    resources = [tuple(r) for r in resources if tuple(r) not in obstacles]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    best = None
    best_score = -10**18

    has_res = len(resources) > 0
    target_list = resources if has_res else [(ox, oy)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Lower distance to chosen target is better.
        if has_res:
            best_to_res = min(dist((nx, ny), r) for r in resources)
            # Prefer getting closer to resources, but keep a bit of pressure on opponent.
            s = -best_to_res
            s += -dist((nx, ny), (ox, oy)) * 0.01
        else:
            # No resources known: chase opponent directly.
            s = -dist((nx, ny), (ox, oy))

        if best is None or s > best_score:
            best_score = s
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best