def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

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
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    best = None
    best_score = None

    # Focus on a small deterministic subset: nearest-to-me few cells to reduce noise.
    res_sorted = sorted(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))
    res_subset = res_sorted[:min(6, len(res_sorted))]

    for dx, dy, nx, ny in candidates:
        total = 0.0
        # Prefer states where we can win contested resources earlier; discourage giving opponent advantage.
        for tx, ty in res_subset:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # If both can reach, prioritize resources where we have a margin; if opponent closer, penalize.
            margin = od - sd
            # Also small preference for nearer resource overall.
            total += (10.0 * margin) - (0.3 * sd) + (0.02 * (tx - tx * 0 + ty * 0))  # stable no-op tie source
        # Tie-break: prefer moves that keep us closer to some resource rather than wander.
        near_best = min(cheb(nx, ny, tx, ty) for tx, ty in res_subset)
        total += -0.1 * near_best
        # Deterministic tie-break by move ordering
        tie = (dx, dy)
        if best_score is None or total > best_score or (total == best_score and tie < best):
            best_score = total
            best = tie

    return [best[0], best[1]]