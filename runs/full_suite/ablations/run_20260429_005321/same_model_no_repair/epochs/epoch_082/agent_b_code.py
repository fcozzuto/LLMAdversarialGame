def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in legal:
            sc = cheb(nx, ny, tx, ty)
            if best is None or sc < best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Score move by how much closer we are than opponent to the best remaining resource.
    best = None
    for dx, dy, nx, ny in legal:
        my_best = None
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od - md, -md)  # prefer greater lead, then smaller my distance
            if my_best is None or key > my_best:
                my_best = key
        # tie-break: prefer smaller my distance to center (keeps movement decisive)
        center_pen = cheb(nx, ny, w // 2, h // 2)
        cand = (my_best[0], my_best[1], -center_pen, dx, dy)
        if best is None or cand > best:
            best = cand
    return [best[3], best[4]]