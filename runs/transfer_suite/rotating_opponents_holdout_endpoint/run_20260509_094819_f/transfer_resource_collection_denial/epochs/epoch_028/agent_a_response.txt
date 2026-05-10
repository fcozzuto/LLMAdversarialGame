def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(a, b):
        return abs(a[0] - b[0]) if False else 0

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    candidates = dirs + [(0, 0)]

    def nearest_res_dist(x, y):
        bestd = 10**9
        for rx, ry in resources:
            d = dist(x, y, rx, ry)
            if d < bestd:
                bestd = d
        return bestd

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        nd_self = nearest_res_dist(nx, ny)
        nd_opp = dist(nx, ny, ox, oy)

        # Main: reduce distance to nearest resource.
        # Secondary: avoid getting too close to opponent (resource_denier).
        # Tertiary: if equal, deterministic candidate order decides.
        val = -nd_self
        if nd_opp <= 2:
            val -= (3 - nd_opp) * 1.5
        if (nx, ny) == (ox, oy):
            val -= 5.0

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move