def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Deterministic fallback: move that maximizes distance from opponent while staying valid
        bestm = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < bestm):
                bestv, bestm = v, (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    best_move = (0, 0)
    best_val = -10**18

    # Strategy: for each candidate move, pick the resource that makes opponent least competitive,
    # then choose the move maximizing (opp_distance - self_distance) with a strong preference for fast self.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_target_val = -10**18
        for tx, ty in resources:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Huge preference: deny opponent (large d_opp). Secondary: reach quickly (small d_self).
            v = d_opp * 100 - d_self * 10
            # Tiebreaker: slightly prefer central targets deterministically.
            cx, cy = W // 2, H // 2
            v -= cheb(tx, ty, cx, cy)
            if v > best_target_val:
                best_target_val = v

        # Also add a mild term to keep some pressure: prefer closer resources overall if denial ties.
        pressure = 0
        for tx, ty in resources:
            d_self = cheb(nx, ny, tx, ty)
            if pressure == 0 or d_self < pressure:
                pressure = d_self
        total = best_target_val - pressure

        if total > best_val or (total == best_val and (dx, dy) < best_move):
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]