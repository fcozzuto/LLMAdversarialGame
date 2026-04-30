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

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources or not inb(sx, sy):
        return [0, 0]

    best = None
    best_score = 10**9
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        d_us = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; otherwise avoid.
        score = d_us * 2 + max(0, d_us - d_op) * 3 - (1 if d_op == d_us else 0)
        if score < best_score:
            best_score = score
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_to = cheb(nx, ny, tx, ty)
            d_opn = cheb(nx, ny, ox, oy)
            # Break ties toward moves that reduce our distance to target, then keep opponent at distance.
            cand.append((d_to, -d_opn, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    return [int(cand[0][2]), int(cand[0][3])]