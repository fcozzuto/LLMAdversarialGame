def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((int(o[0]), int(o[1])))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                valid_res.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (x, y) in obs:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    if not valid_res:
        for dx, dy in [(1, 1), (1, 0), (0, 1), (0, 0), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Pick resource where we're comparatively closer than the opponent.
    best = None
    for rx, ry in valid_res:
        myd = cheb(x, y, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        score = (myd - opd, myd, rx, ry)  # prefer smaller gap, then closer
        if best is None or score < best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    # Greedy step: decrease my distance to target; also prefer moving away from opponent.
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        # lexicographic: primary minimize myd, then maximize opponent distance, then tie-break by coord
        val = (myd, -opd, nx, ny, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]