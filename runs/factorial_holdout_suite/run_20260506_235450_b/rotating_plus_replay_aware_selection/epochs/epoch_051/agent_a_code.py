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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we can arrive earlier with larger margin; otherwise least losing.
        key = (do - ds, -do, -ds)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Choose move that best improves "race margin" and closeness to chosen target.
    best_move = None
    for dx, dy, nx, ny in legal:
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        margin = do - ds
        # Also mildly prefer moves that increase our distance from opponent to counter sweeping.
        opp_sep = cheb(nx, ny, ox, oy)
        key = (margin, -ds, opp_sep)
        if best_move is None or key > best_move[0]:
            best_move = (key, dx, dy)
    return [int(best_move[1]), int(best_move[2])]