def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    if resources:
        pts = []
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                pts.append((int(r[0]), int(r[1])))
        if not pts:
            pts = [(sx, sy)]
    else:
        pts = [(sx, sy)]

    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Evaluate: prefer getting closer to a resource that opponent isn't as close to.
        val = None
        for rx, ry in pts:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            score = ds - 0.6 * do
            if val is None or score < val:
                val = score
        # Fallback: if somehow all resources invalid, just move toward opponent.
        if val is None:
            val = dist(nx, ny, ox, oy)
        key = (val, dist(nx, ny, ox, oy), dx, dy)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = int(sx) + dx, int(sy) + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best_move