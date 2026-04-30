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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose best target resource for advantage: (opp_dist - self_dist), tie-break by being closer, then by coordinates.
    best_t = None
    best_key = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        key = (od - sd, -sd, -x, -y)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_t = (x, y)

    tx, ty = best_t
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    # Evaluate one-step moves by expected advantage after moving toward/away from target.
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # Primary: increase advantage toward target; Secondary: reduce distance to target; Tertiary: avoid getting farther from current target.
        key = (od2 - sd2, -sd2, -abs((tx - nx)) - abs((ty - ny)), -dx, -dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move