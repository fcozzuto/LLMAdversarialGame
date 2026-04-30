def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if o is not None and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return x < 0 or y < 0 or x >= w or y >= h or (x, y) in obstacles

    resources.sort(key=lambda p: cheb(sx, sy, p[0], p[1]))
    targets = resources[:3]

    best_dx, best_dy = 0, 0
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Primary: minimize distance to nearest of a few best targets.
        d_to = cheb(nx, ny, targets[0][0], targets[0][1])
        if len(targets) > 1:
            d_to = min(d_to, cheb(nx, ny, targets[1][0], targets[1][1]))
        if len(targets) > 2:
            d_to = min(d_to, cheb(nx, ny, targets[2][0], targets[2][1]))
        # Secondary: avoid giving opponent advantage (prefer staying farther from opponent).
        d_opp = cheb(nx, ny, ox, oy)
        val = d_to * 100 - d_opp
        if best_val is None or val < best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    if blocked(sx, sy):
        return [0, 0]
    return [best_dx, best_dy]