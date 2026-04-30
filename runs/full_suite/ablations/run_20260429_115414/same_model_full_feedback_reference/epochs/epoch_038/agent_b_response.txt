def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Target resource where we can beat the opponent by the largest margin (reach earlier).
    best_r = None
    best_margin = -10**9
    for rx, ry in resources:
        d_me = kdist(sx, sy, rx, ry)
        d_op = kdist(ox, oy, rx, ry)
        margin = d_op - d_me  # positive means we are closer
        # Slight preference for earlier overall arrival to avoid indecision.
        arrival = -(d_me + 0.1 * d_op)
        score = 1000 * margin + arrival
        if score > best_margin:
            best_margin = score
            best_r = (rx, ry)

    rx, ry = best_r

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break order: prefer straight/diagonal progress toward target, then minimal distance.
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me_next = kdist(nx, ny, rx, ry)
        d_op_now = kdist(ox, oy, rx, ry)
        # If we step onto (or closer than) opponent would, boost; also penalize moving away.
        prog = (kdist(sx, sy, rx, ry) - d_me_next)
        margin_next = d_op_now - d_me_next
        # Obstacle-aware soft check: avoid moves that allow opponent to instantly get another resource sooner.
        # Use only local info (two candidate resources) for determinism and brevity.
        opp_gain = 0
        for j in range(min(2, len(resources))):
            r2x, r2y = resources[j]
            if kdist(r2x, r2y, ox, oy) <= kdist(r2x, r2y, nx, ny):
                opp_gain += 1
        val = 1000 * margin_next + 50 * prog - 3 * opp_gain - 0.01 * d_me_next
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]