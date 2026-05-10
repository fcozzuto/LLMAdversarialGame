def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    bestkey = None
    for r in res:
        sd = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        adv = od - sd  # positive means we are closer/equal
        key = (adv, -sd, -r[0], -r[1])
        if bestkey is None or key > bestkey:
            bestkey = key
            best = r
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in obs:
            continue
        nds = cheb((nx, ny), (tx, ty))
        ndv = cheb((ox, oy), (tx, ty)) - nds
        # Prefer reducing distance; if equal, prefer higher contest advantage; then deterministic coords
        key = (-(nds), ndv, -(dx * dx + dy * dy), -nx, -ny)
        if bestmk is None or key > bestmk:
            bestmk = key
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]