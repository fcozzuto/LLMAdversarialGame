def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources", []) or []
    cur = []
    for r in resources:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                cur.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not cur:
        return [0, 0]

    # Prefer capturing resources we can reach no later (opponent advantage), else reduce deficit.
    best = None
    best_key = None
    for rx, ry in cur:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd  # positive means we are closer/equal
        # Key: maximize margin, then smaller self distance, then deterministic coordinate.
        key = (-margin, sd, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best

    # Greedy step: choose move that keeps us best versus the chosen target; avoid obstacles.
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d_to = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Score: minimize distance to target; if tie, maximize our closeness over opponent (favor not falling behind).
            score = (d_to, -cheb(nx, ny, tx, ty) + d_opp, nx, ny, dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]

    # If all blocked/unconsidered, stay.
    if best_score is None:
        return [0, 0]
    return best_move