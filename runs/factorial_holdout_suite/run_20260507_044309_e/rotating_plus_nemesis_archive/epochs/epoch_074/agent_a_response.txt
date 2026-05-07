def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        min_ds = 10**9
        min_do = 10**9
        closer = 0
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < min_ds:
                min_ds = ds
            if do < min_do:
                min_do = do
            if ds <= do:
                closer += 1

        # Prefer making progress (smaller min_ds), and prefer resources we can contest/secure (ds<=do).
        score = (-min_ds * 10) + (closer * 3) + (-min_do) + (-(dx * dx + dy * dy))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]