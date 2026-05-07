def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            rr = (int(r[0]), int(r[1]))
            if rr not in obstacles:
                resources.append(rr)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def step_towards(tx, ty):
        best = (10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, (dx, dy))
        return best[1]

    if not resources:
        # Prefer moving away from opponent row/col if stuck
        cand = sorted(
            [(md(sx + dx, sy + dy, ox, oy), (dx, dy)) for dx, dy in moves if legal(sx + dx, sy + dy)],
            key=lambda x: x[0],
        )
        return cand[0][1] if cand else [0, 0]

    # Opponent archetype: sweep_rows -> discourage contesting same row neighborhood
    best_move = [0, 0]
    best_val = -10**18
    for tx, ty in resources:
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        row_dist = abs(ty - oy)
        # Big reward if we can arrive first; otherwise steer toward "uncontested" resources
        val = 0
        if myd < opd:
            val += 100000
        else:
            val += (opd - myd) * 50
        # Make it robust vs row-sweeping opponent: prefer far rows, slightly prefer closer points
        val += row_dist * 40 - myd * 5
        # Small preference for resources not in immediate opponent-reachable band
        if abs(ty - oy) <= 1 and myd >= opd:
            val -= 200
        if val > best_val:
            best_val = val
            best_move = step_towards(tx, ty)

    return [int(best_move[0]), int(best_move[1])]