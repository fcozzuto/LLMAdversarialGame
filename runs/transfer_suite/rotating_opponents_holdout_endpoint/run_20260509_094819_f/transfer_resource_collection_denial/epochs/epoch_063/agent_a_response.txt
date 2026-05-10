def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Heuristic change: avoid giving opponent sweep advantage on their current row.
    off_row = [r for r in resources if r[1] != oy]
    cand = off_row if off_row else resources

    # Prefer resources that are closer to us than to opponent, but strongly bias off-row.
    best = None
    best_key = None
    for x, y in cand:
        ds = cheb(x, y, sx, sy)
        do = cheb(x, y, ox, oy)
        row_bias = 0 if y != oy else 6  # if forced onto opponent row, make it less attractive
        # Secondary: prefer staying away from obstacles by discouraging targets adjacent to obstacles.
        adj_pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) in obstacles:
                    adj_pen = 2
                    break
            if adj_pen:
                break
        key = (ds - do + row_bias + adj_pen, ds, -do, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Deterministic fallback: try orthogonal step; then stay.
        if dx != 0:
            alt = 0 if ty == sy else (1 if ty > sy else -1)
            if (sx, sy + alt) not in obstacles:
                return [0, alt]
        if dy != 0:
            alt = 0 if tx == sx else (1 if tx > sx else -1)
            if (sx + alt, sy) not in obstacles:
                return [alt, 0]
        return [0, 0]
    return [dx, dy]