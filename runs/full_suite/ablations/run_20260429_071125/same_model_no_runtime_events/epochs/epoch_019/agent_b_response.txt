def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]
    if not valid(sx, sy):
        if valid(0, 0):
            sx, sy = 0, 0
        else:
            return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Choose a target resource we are likely to reach first; break ties deterministically.
    best = None
    best_key = None
    for rx, ry in resources:
        if not valid(rx, ry) and (rx, ry) != (sx, sy):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If opponent is closer (or equal), penalize to reduce contest losses.
        penalty = 0
        if do <= ds:
            penalty = 100 + (ds - do) * 2
        key = (ds + penalty, -do, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key

    if best is None:
        return [0, 0]
    tx, ty = best

    # Greedy step: minimize distance to target, while maximizing distance from opponent; avoid obstacles.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = [0, 0]
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dtt = cheb(nx, ny, tx, ty)
        too = cheb(nx, ny, ox, oy)
        # Primary: closer to target; Secondary: keep away from opponent; Tertiary: deterministic tie-break.
        val = (dtt, -too, dx, dy)
        if bestv is None or val < bestv:
            bestv = val
            bestm = [dx, dy]
    return [int(bestm[0]), int(bestm[1])]