def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        # Fallback: drift toward opponent's corner-ward to contest space
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    # Choose a resource: strongly prefer ones I'm closer to; if both close, pick the one that limits opponent.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = man(rx, ry, sx, sy)
        opd = man(rx, ry, ox, oy)
        # Higher is better: maximize (opponent advantage if any) while keeping my distance small.
        # Add tiny tie-break favoring corners-ish (deterministic).
        corner_bias = (rx == 0 or rx == w - 1) + (ry == 0 or ry == h - 1)
        key = (opd - myd, -myd, corner_bias, -((rx * 31 + ry * 17) % 997))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        myd = man(nx, ny, tx, ty)
        # If multiple paths to target, prefer steps that also keep opponent farther from it.
        opd_next = man(tx, ty, ox, oy)
        # Also mild anti-blocking: avoid stepping onto cells adjacent to many obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px = nx + ax
                py = ny + ay
                if (px, py) in obstacles:
                    adj += 1

        score = (-myd, (opd_next - myd), -adj, (dx == 0 and dy == 0), -((nx * 13 + ny * 7) % 101))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]