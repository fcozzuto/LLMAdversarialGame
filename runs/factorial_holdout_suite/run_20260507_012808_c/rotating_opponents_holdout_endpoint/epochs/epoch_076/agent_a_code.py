def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Targeting change: when opponent is closer/equal, de-prioritize that resource and go for a "safer" one.
    best = None
    for rx, ry in resources:
        sd = man(rx, ry, sx, sy)
        od = man(rx, ry, ox, oy)
        # If opponent is closer, penalize more strongly to avoid chasing denier-preferred points.
        rel = od - sd
        score = (rel * 2) - (0 if rel > 0 else (sd + 3))  # push for rel>0, flee rel<=0
        # tie-break: prefer lower opponent proximity and "north/west" deterministically
        tieb = (od, ry, rx, sd)
        key = (score, -tieb[0], -tieb[1], -tieb[2], -tieb[3])
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # One-step move: greedy towards target; tie-break by increasing opponent's distance to the same target.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # how much this move changes opponent's relative situation (self-only move)
        # tie-break with deterministic ordering that avoids jitter
        d_opp_after = d_opp  # unchanged, but keep structure consistent
        key = (-d_self, d_opp_after, ny, nx)
        if bestm is None or key > bestm[0]:
            bestm = (key, (dx, dy))
    return [int(bestm[1][0]), int(bestm[1][1])]