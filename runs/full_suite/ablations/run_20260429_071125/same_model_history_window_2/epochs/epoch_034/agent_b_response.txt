def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    rc = observation.get("remaining_resource_count", None)
    try:
        rc = int(rc)
    except:
        rc = len(resources)

    aggressive = 1 if rc is not None and rc <= 4 else 0
    k_avoid = 6 if aggressive else 3

    # Pick target deterministically: minimize (our distance - opponent advantage).
    # If contested, bias toward closer resources to reduce opponent lead.
    best_t = (sx, sy)
    best_score = 10**9
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Lower is better for us
        score = ds * 10 - (do - ds) * (3 if aggressive else 1)
        if score < best_score:
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        dto = cheb(ox, oy, tx, ty)

        # If opponent is closer to the target, avoid giving them easier approach;
        # otherwise, advance toward target.
        opp_ahead = 1 if dto < ds else 0
        val = ds * 1000 + (k_avoid * (1 if do <= 2 else 0)) + (800 if opp_ahead and aggressive else 0)

        # Mild tie-breaker: prefer moving into better relative position vs opponent.
        if do <= 3:
            val += cheb(nx, ny, ox, oy) * (20 if aggressive else 10)

        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]