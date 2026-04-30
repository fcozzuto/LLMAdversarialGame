def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, dict):
            if "pos" in r and r["pos"] and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    best_res = resources[0]
    best_val = 10**9
    for rx, ry in resources:
        dself = cheb(sx, sy, rx, ry)
        dold = cheb(ox, oy, rx, ry)
        val = dself - 0.9 * dold
        if val < best_val:
            best_val = val
            best_res = (rx, ry)

    rx, ry = best_res
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    curd = cheb(sx, sy, rx, ry)
    if curd == 0:
        return [0, 0]

    best_move = (0, 0)
    best_eval = 10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, rx, ry)
        opdist = cheb(nx, ny, ox, oy)
        evalv = nd - 0.05 * opdist
        if evalv < best_eval or (evalv == best_eval and (dx, dy) < best_move):
            best_eval = evalv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]