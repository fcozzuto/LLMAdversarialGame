def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            obstacles.add((int(p["x"]), int(p["y"])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a >= b else b

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    best = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            rx, ry = int(r["x"]), int(r["y"])
        else:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (0 if ds < do else 1, ds - do, ds)
        if best is None or score < best[0]:
            best = (score, rx, ry)
    if best is None:
        return [0, 0]

    tx, ty = best[1], best[2]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        score = (0 if ds < do else 1, ds, dx * dx + dy * dy)
        if score < best_move:
            best_move = (score, dx, dy)
    return [int(best_move[1]), int(best_move[2])]