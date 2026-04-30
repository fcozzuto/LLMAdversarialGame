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
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif ("x" in r and "y" in r and r["x"] is not None and r["y"] is not None):
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

    # Pick target: prefer closer to self and farther from opponent, deterministically.
    best_t = None
    best_val = -10**9
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        # slight tie-break to center to avoid dithering
        cx, cy = w // 2, h // 2
        center = -cheb(rx, ry, cx, cy)
        val = (-d1) + 0.35 * d2 + 0.05 * center
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = [0, 0]
    best_s = -10**9

    def obstacle_adj_pen(x, y):
        # small penalty for being adjacent to obstacle to encourage avoidance
        pen = 0
        for ax, ay in obstacles:
            if cheb(x, y, ax, ay) == 1:
                pen += 1
        return pen

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s_to_t = cheb(nx, ny, tx, ty)
        s_from_o = cheb(nx, ny, ox, oy)
        # if opponent is very close, temporarily prioritize distance to it
        opp_close = 1 if cheb(sx, sy, ox, oy) <= 2 else 0
        score = (-s_to_t) + 0.20 * s_from_o + 0.35 * opp_close * s_from_o - 0.10 * obstacle_adj_pen(nx, ny)
        if score > best_s:
            best_s = score
            best_m = [dx, dy]

    return [int(best_m[0]), int(best_m[1])]