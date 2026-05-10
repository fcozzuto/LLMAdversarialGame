def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def to_xy(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return int(q[0]), int(q[1])
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return None

    obs_set = set()
    for p in obstacles:
        xy = to_xy(p)
        if xy is not None:
            x, y = xy
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    res = []
    for r in resources:
        xy = to_xy(r)
        if xy is not None:
            x, y = xy
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best_cell = None
    best_val = -10**9
    for x, y in res:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # maximize advantage; tie-break prefer closer to self
        val = (od - sd) * 1000 - sd
        if val > best_val:
            best_val = val
            best_cell = (x, y)

    tx, ty = best_cell

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # deterministic tie-breaking order already defined by deltas list
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # prefer reducing distance to target while maintaining/creating advantage
        score = (d_opp - d_to_target) * 1000 - d_to_target
        # small bias toward staying aligned with target to avoid oscillations deterministically
        score -= abs((nx - tx) - (ny - ty)) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move == (0, 0):
        # if all moves blocked, must stay; otherwise return computed best.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]