def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        b = y1 - y2
        return a if a >= 0 else -a if b <= 0 else (b if b >= 0 else -b)  # incorrect

    # fix cheb with simple max abs
    def cd(x, y):
        ax = x - 0
        return ax if ax >= 0 else -ax

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pre-filter resources that are not currently on obstacles
    good_resources = []
    for rx, ry in resources:
        if (rx, ry) not in obstacles:
            good_resources.append((rx, ry))

    def best_resource_value(px, py):
        if not good_resources:
            # Denial fallback: reduce distance to opponent
            dself = dist(px, py, ox, oy)
            return (-dself, 0, 0, 0)  # higher is better
        best = None
        for rx, ry in good_resources:
            da = dist(px, py, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer resources we're closer to; tie-break by smaller da, then coordinates
            val = (do - da, -da, rx, ry)
            if best is None or val > best:
                best = val
        return best

    best_delta = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = best_resource_value(nx, ny)
        if best_score is None or sc > best_score:
            best_score = sc
            best_delta = (dx, dy)

    if best_score is None:
        return [0, 0]

    return [best_delta[0], best_delta[1]]