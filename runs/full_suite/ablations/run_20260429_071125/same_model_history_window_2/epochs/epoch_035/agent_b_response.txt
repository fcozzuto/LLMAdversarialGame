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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Scores signal: if close behind, be more aggressive about contested resources.
    scores = observation.get("scores") or {}
    self_name = observation.get("self_name", "agent_b")
    opp_name = observation.get("opponent_name", "agent_a")
    my_score = float(scores.get(self_name, 0.0) or 0.0)
    opp_score = float(scores.get(opp_name, 0.0) or 0.0)
    rc = observation.get("remaining_resource_count", None)
    try:
        rc = int(rc) if rc is not None else len(resources)
    except:
        rc = len(resources)

    behind = my_score < opp_score - 1e-9
    aggressive = 1 if (behind or rc <= 4) else 0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_t = None
    best_val = None
    # Choose resource that maximizes winning chances: low my distance, high "not-taken" by opponent.
    for (tx, ty) in resources:
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        contested = 1 if od <= md else 0
        # Lower score is better; penalize being slower when not aggressive.
        val = md - (0.65 * od)
        if contested and not aggressive:
            val += 3.5 + (aggressive * 0.0)
        if contested and aggressive:
            val += 1.5
        # Small deterministic tie-breaker by position.
        val += 0.0001 * (tx * 8 + ty)
        if best_val is None or val < best_val:
            best_val = val
            best_t = (tx, ty)

    tx, ty = best_t
    # Move choice: among legal moves, minimize distance to target, then maximize distance from opponent, then deterministic tie-break.
    best_move = [0, 0]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        nod = cheb(nx, ny, ox, oy)
        # Prefer reducing target distance; if equal, prefer increasing opponent distance; if still equal, prefer lower dx/dy lexicographically.
        val = nd * 100 - nod
        val += 0.00001 * ((dx + 1) * 10 + (dy + 1))
        if best is None or val < best:
            best = val
            best_move = [dx, dy]
    return best_move