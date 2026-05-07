def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    ti = int(observation.get("turn_index", 0) or 0)

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

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Fallback: move toward opponent (keeps pressure) or stay if blocked
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = man(nx, ny, ox, oy)
                if d < best[0]:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    best_val = -10**18
    best_t = resources[0]
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        gap = od - sd  # positive means we're closer
        # Prefer taking resources we're closer to; break ties by higher gap then smaller self distance
        val = gap * 100 - sd * 3 - ((rx * 31 + ry * 17 + ti) % 3)
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t
    # Greedy one-step toward chosen target, but deterministic tie-breaking
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nd = man(nx, ny, tx, ty)
            # Strongly prefer moving onto resources (if visible) and improving approach
            onto = 1 if (nx, ny) == (tx, ty) else 0
            approach = man(sx, sy, tx, ty) - nd
            score = onto * 10**6 + approach * 1000 - nd + (ti % 7) * 0.0001 - (dx * dx + dy * dy) * 0.01
            if score > best[0]:
                best = (score, dx, dy)

    return [int(best[1]), int(best[2])]