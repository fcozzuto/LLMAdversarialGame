def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def score_move(nx, ny):
        d = cheb(nx, ny, ox, oy)
        # obstacle proximity penalty (deterministic)
        prox = 0
        for ax, ay in obstacles:
            prox += 2 if cheb(nx, ny, ax, ay) == 0 else (1 if cheb(nx, ny, ax, ay) == 1 else 0)
        # if near obstacle, avoid; also avoid reducing movement toward/away when possible
        return (-d - 5 * prox) if is_evader else (d - 5 * prox)

    best = None
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = score_move(nx, ny)
        if best_s is None or s > best_s:
            best_s = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]