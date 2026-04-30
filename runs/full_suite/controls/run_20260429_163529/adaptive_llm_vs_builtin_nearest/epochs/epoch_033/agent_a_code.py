def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))

    best_overall_move = (0, 0)
    best_overall_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate best target after this move: prefer resources where we are relatively closer.
        best_key = None
        for tx, ty in res:
            dm = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Winning margin: smaller is better; add tiny tie-break to prefer earlier capture and safer lines.
            key = (dm - do, dm + 0.01 * (tx + ty), dm)
            if best_key is None or key < best_key:
                best_key = key

        score = best_key[0]
        if best_overall_score is None or score < best_overall_score or (score == best_overall_score and best_key < best_overall_key):
            best_overall_score = score
            best_overall_move = (dx, dy)
            best_overall_key = best_key

    return [int(best_overall_move[0]), int(best_overall_move[1])]