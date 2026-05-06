def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_step(fromx, fromy, tx, ty):
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = fromx + dx, fromy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                nx, ny = fromx, fromy
            d = cheb(nx, ny, tx, ty)
            # deterministic tie-break: prefer smaller (d, nx, ny)
            cand = (d, nx, ny, 0)
            if cand < best:
                best = cand
                best_dx, best_dy = dx, dy
        return best_dx, best_dy

    # Pick a target resource likely to be contested: maximize (opp_dist - self_dist).
    best_t = None
    best_val = (-10**9, -10**9)
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # If close for us, strongly prefer; if opponent closer, still prefer only if we can gain by next step.
        val = (od - sd, -sd)
        if val > best_val:
            best_val = val
            best_t = (tx, ty)
    tx, ty = best_t

    # Evaluate our possible move predicting opponent response toward same target.
    best_score = (-10**9, -10**9)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy
        our_d = cheb(nx, ny, tx, ty)

        # predict opponent next step toward target
        odx, ody = best_step(ox, oy, tx, ty)
        onx, ony = ox + odx, oy + ody
        if onx < 0 or onx >= w or ony < 0 or ony >= h or (onx, ony) in obstacles:
            onx, ony = ox, oy
        opp_d = cheb(onx, ony, tx, ty)

        # prioritize becoming closer than opponent; also prefer reaching exact cell.
        score = (opp_d - our_d, -(our_d) if our_d == 0 else -our_d)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]