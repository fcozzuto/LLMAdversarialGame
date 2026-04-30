def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not (0 <= sx < w and 0 <= sy < h) or not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a target that we can reach earlier; if none, contest the closest.
    best_score = None
    best_t = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer positive lead; otherwise minimize our distance, with deterministic tie-break.
        lead = do - ds
        score = (lead, -ds, -(rx + 31 * ry))
        if best_score is None or score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t
    # Evaluate all local moves (including stay) deterministically; avoid obstacles.
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_m = None
    best_mscore = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        # Add a small penalty for giving opponent a closer angle to the same target.
        dopp = cheb(ox, oy, tx, ty)
        # Also mildly prefer moving away from opponent to reduce contest volatility.
        dopp_self = cheb(nx, ny, ox, oy)
        mscore = (-dself, -lead if (lead := (dopp - cheb(nx, ny, tx, ty))) is not None else 0, -dopp_self, dx*3 + dy)
        if best_mscore is None or mscore > best_mscore:
            best_mscore = mscore
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]