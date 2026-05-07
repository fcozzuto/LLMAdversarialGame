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

    def diag_dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Deterministic fallback: move toward center to avoid getting stuck.
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = diag_dist(tx, ty, nx, ny)
                if (d, dx, dy) < best:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    # Pick a target I can reach earlier than the opponent; tie-break deterministically.
    resources_sorted = sorted(resources, key=lambda t: (t[0], t[1]))
    best_score = -10**18
    best_target = resources_sorted[0]
    for rx, ry in resources_sorted:
        myd = diag_dist(rx, ry, sx, sy)
        opd = diag_dist(rx, ry, ox, oy)
        # Prefer winning the resource (opponent farther), then closer.
        score = (opd - myd) * 10 - myd
        # Small bias to reduce risk near opponent: if I’m not winning, pick less-available targets.
        if opd <= myd:
            score -= 5
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    # Choose a legal move that minimizes distance to target.
    best = (10**9, 2, 2)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = diag_dist(tx, ty, nx, ny)
            if (d, dx, dy) < best:
                best = (d, dx, dy)

    return [best[1], best[2]]