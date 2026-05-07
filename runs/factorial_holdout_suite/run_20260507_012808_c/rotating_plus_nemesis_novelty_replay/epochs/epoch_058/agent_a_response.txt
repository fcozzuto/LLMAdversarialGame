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

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w // 2), (h // 2)
    else:
        # Target resources we are relatively closer to; break ties deterministically by position.
        best = None
        for rx, ry in resources:
            dm = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources where (my distance - opponent distance) is small/negative.
            val = dm - 0.95 * do
            # Deterministic micro-bias to reduce cycling.
            val += 0.001 * ((rx * 31 + ry * 17 + ti) % 97)
            if best is None or val < best[0] or (val == best[0] and (rx, ry) < best[1]):
                best = (val, (rx, ry))
        tx, ty = best[1]

    best_move = (0, 0, 10**9)  # dx,dy,score
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # Evaluate next step with same target; add opponent pressure term.
            dm2 = man(nx, ny, tx, ty)
            do2 = man(ox, oy, tx, ty)
            score = dm2 - 0.95 * do2 + 0.0001 * ((nx * 19 + ny * 23 + ti) % 61)
            # Small reward for reducing distance to nearest resource set (robustness).
            if resources:
                score += 0.02 * min(man(nx, ny, rx, ry) for (rx, ry) in resources)
            if score < best_move[2]:
                best_move = (dx, dy, score)
    return [best_move[0], best_move[1]]