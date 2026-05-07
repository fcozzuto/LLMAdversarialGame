def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
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

    # Pick target where we are ahead (lower me_dist - opp_dist); tie-break on smaller me_dist.
    best = None
    best_key = None
    for x, y in resources:
        d_me = cheb(sx, sy, x, y)
        d_op = cheb(ox, oy, x, y)
        key = (d_me - d_op, d_me, cheb(ox, oy, x, y))
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    # Move: choose a legal delta that most improves our race advantage toward the target.
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    bestm = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_me2 = cheb(nx, ny, tx, ty)
        d_op2 = cheb(ox, oy, tx, ty)  # opponent position doesn't change this turn
        # Primary: reduce our distance to target; Secondary: increase our advantage (d_op2 - d_me2).
        adv = d_op2 - d_me2
        # Tertiary: prefer staying more central to avoid getting boxed.
        cent = -(((nx - cx) ** 2) + ((ny - cy) ** 2))
        val = (d_me2, -adv, -cent)
        if bestv is None or val < bestv:
            bestv = val
            bestm = [dx, dy]

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]