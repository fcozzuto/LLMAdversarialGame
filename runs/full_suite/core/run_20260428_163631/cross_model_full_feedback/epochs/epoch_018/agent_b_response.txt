def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # candidate moves (dx, dy)
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # distance helpers
    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # filter resources inside and not on obstacle
    res = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if inb(rx, ry) and (rx, ry) not in obstacles:
            res.append((rx, ry))

    # If there are resources, prefer moving toward nearest resource while avoiding opponent
    if res:
        # choose nearest resource
        nearest = min(res, key=lambda p: cheb(p[0], p[1], sx, sy))
        best = None
        best_score = None
        for dx, dy, nx, ny in cand:
            dist = cheb(nearest[0], nearest[1], nx, ny)
            to_opp = cheb(ox, oy, nx, ny)
            # score: prefer closer to resource, while staying away from opponent
            score = -dist + (to_opp * 0.0)  # primary is distance to resource
            # add small bias to move away if possible
            if nx == ox and ny == oy:
                score -= 100
            if best is None or score > best_score:
                best = (dx, dy, nx, ny)
                best_score = score
        return [best[0], best[1]]

    # No resources: simple deterministic rule
    # Move to reduce proximity to opponent when possible, else stay
    best = None
    best_score = None
    for dx, dy, nx, ny in cand:
        dist_to_opp = cheb(nx, ny, ox, oy)
        # prefer maximizing distance to opponent
        score = dist_to_opp
        if (nx, ny) == (ox, oy):
            score -= 100
        if best is None or score > best_score:
            best = (dx, dy, nx, ny)
            best_score = score
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]