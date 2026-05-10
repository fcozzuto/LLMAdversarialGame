def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        best_move = None
        best_val = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dcent = abs(nx - cx) + abs(ny - cy)
            val = (dcent, abs(nx - ox) + abs(ny - oy))
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_cell = None
    best_key = None
    for x, y in resources:
        sd = man(sx, sy, x, y)
        od = man(ox, oy, x, y)
        # Prefer resources where we are closer than opponent; break ties by closer-to-self, then by deterministic cell order.
        key = (sd - od, sd, abs(x - cx) + abs(y - cy), x, y)
        if best_key is None or key < best_key:
            best_key = key
            best_cell = (x, y)

    tx, ty = best_cell
    if tx == sx and ty == sy:
        return [0, 0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If that direct move is illegal, choose the legal move that decreases sd most (with opponent-progress tie-break).
    cand = (dx, dy)
    if cand in legal:
        return [int(cand[0]), int(cand[1])]

    best_move = None
    best_val = None
    for mdx, mdy in legal:
        nx, ny = sx + mdx, sy + mdy
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        val = (sd - od, sd, abs(nx - cx) + abs(ny - cy), mdx, mdy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (mdx, mdy)
    return [int(best_move[0]), int(best_move[1])]