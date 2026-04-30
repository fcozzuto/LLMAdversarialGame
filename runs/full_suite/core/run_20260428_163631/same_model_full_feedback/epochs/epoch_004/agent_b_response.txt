def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    # Deterministic target selection: prefer resources where we're closer than opponent, weighted by distance gap.
    for rx, ry in resources:
        if not inb(rx, ry): 
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd  # positive means advantage
        # Tie-break deterministically by ( -gap, sd, rx, ry ) via lexicographic min
        key = (-gap, sd, rx, ry)
        sc = gap * 100 - sd
        if best_score is None or key < best_score:
            best_score = key
            best = (rx, ry)

    tx, ty = (sx, sy) if best is None else best

    # If adjacent to a resource, step onto it.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if safe(nx, ny) and any(nx == r[0] and ny == r[1] for r in resources):
            return [dx, dy]

    # If no resources remain: move to contest by approaching opponent while avoiding obstacles.
    if not resources:
        tx, ty = ox, oy

    # Greedy move to reduce distance to target; if blocked, choose best alternative that still improves or least harms.
    curd = cheb(sx, sy, tx, ty)
    best_move = [0, 0]
    best_val = (-10**9, sx, sy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        improve = curd - nd
        # Prefer improvement; then prefer moves that also increase distance from opponent to reduce contest losses.
        od = cheb(nx, ny, ox, oy)
        myadv = od - nd
        key = (-improve, -myadv, nd, nx, ny)
        val = (key, dx, dy)
        if val[0] < best_val:
            best_val = val[0]
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]