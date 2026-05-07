def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not resources or not legal:
        return [0, 0]

    best = None  # (score1, score2, score3, tx, ty, mdx, mdy)
    for mdx, mdy, nx, ny in legal:
        # Choose the resource that gives best immediate "race" advantage from (nx, ny)
        best_for_move = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            cand = (adv, -ds, -((rx + ry) & 1), rx, ry)  # deterministic within move
            if best_for_move is None or cand > best_for_move:
                best_for_move = cand
        adv, negds, _, rx, ry = best_for_move
        ds2 = -negds
        key = (adv, -ds2, 0, rx, ry, mdx, mdy)
        if best is None or key > best:
            best = key

    return [int(best[5]), int(best[6])]