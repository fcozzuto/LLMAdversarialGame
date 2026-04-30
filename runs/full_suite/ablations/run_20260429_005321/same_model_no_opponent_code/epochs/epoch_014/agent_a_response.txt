def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if blocked(nx, ny):
            continue
        if resources:
            # choose move that maximizes "chances" at contested/soonest resources
            # score uses both own distance and opponent distance; tie-breaks deterministically
            local_best = None
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # strong bias for resources opponent is closer to (deny) or for which we can beat
                # also penalize moving into longer personal paths
                s = (do - ds) * 10 - ds
                if local_best is None or s > local_best:
                    local_best = s
            score = local_best
        else:
            # no resources: move to reduce distance to opponent corner-ish (deterministic)
            score = -(cheb(nx, ny, 0, 0) + cheb(nx, ny, w - 1, h - 1) * 0.01)
        cand = (score, -dx, -dy, dx, dy)
        if best is None or cand > best:
            best = cand
    if best is None:
        return [0, 0]
    return [int(best[3]), int(best[4])]