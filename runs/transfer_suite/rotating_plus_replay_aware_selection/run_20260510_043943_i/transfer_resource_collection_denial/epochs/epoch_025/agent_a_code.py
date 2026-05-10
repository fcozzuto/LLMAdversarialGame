def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def min_dist_to_resources(x, y):
        md = 10**9
        for rx, ry in resources:
            d = man(x, y, rx, ry)
            if d < md:
                md = d
        return md if md != 10**9 else 10**9

    any_resource = len(resources) > 0
    best = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        dres = min_dist_to_resources(nx, ny) if any_resource else 0
        dold = man(nx, ny, ox, oy)
        score1 = (-dres if any_resource else dold)  # bigger is better
        score2 = dold if any_resource else dold   # maximize distance from opponent
        key = (score1, score2, -dx, -dy)  # deterministic tie-break
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    if blocked(sx, sy):
        return [0, 0]
    return best_move if best is not None else [0, 0]