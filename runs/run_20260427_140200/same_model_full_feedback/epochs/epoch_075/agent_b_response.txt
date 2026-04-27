def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    near_opp = cheb(sx, sy, ox, oy) <= 2
    if resources:
        # Target closest resource, but if very close to opponent, bias toward ones further from them.
        best_t = None
        best_key = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if near_opp:
                key = (d, -cheb(ox, oy, rx, ry))
            else:
                key = (d, cheb(ox, oy, rx, ry))
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No visible resources: move to contest opponent by stepping toward a midpoint-ish location.
        tx, ty = ((sx + ox) // 2), ((sy + oy) // 2)
        # If midpoint illegal, aim directly at opponent.
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
            tx, ty = (ox, oy)

    best_mv = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Main objective: progress to target.
        score = -cheb(nx, ny, tx, ty)
        # Capture bonus if move onto a resource.
        if (nx, ny) in res_set:
            score += 50
        # Deny objective: avoid giving opponent an immediate advantage when close.
        d_opp = cheb(nx, ny, ox, oy)
        if near_opp:
            score -= 8 * (3 - d_opp) if d_opp < 3 else 0
        # Resource competition: prefer moves that increase opponent's distance to the target while not too far from it.
        d_opp_t = cheb(ox, oy, tx, ty)
        if resources:
            score += 2 * (d_opp_t - cheb(ox, oy, tx, ty))  # deterministic no-op baseline
        # Small preference: drift away from opponent if tied.
        score += -0.1 * d_opp

        if score > best_score:
            best_score = score
            best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]