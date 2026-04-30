def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res_list = observation.get("resources", []) or []
    resources = []
    for r in res_list:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    # Opponent is in opposite corner at start, but we use current position if present.
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Select a target resource by maximizing advantage; then choose the move that improves that advantage.
    best_target = None
    best_adv = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = (do - ds)
        # Prefer immediate collection and nearer overall if similar.
        if adv > best_adv or (adv == best_adv and (ds, cheb(rx, ry, 0, 0)) < (cheb(sx, sy, 0, 0), 10**9)):
            best_adv = adv
            best_target = (rx, ry)
    rx, ry = best_target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = cheb(nx, ny, rx, ry)
        # Use opponent current distance as baseline; maximize reduced self distance and immediate capture.
        capture = 1 if (nx, ny) == (rx, ry) else 0
        score = (best_adv * 100) + capture * 10**6 + (best_adv - ds2 + 0.01 * (rx + ry))
        # Secondary: avoid moving away from board center once advantage tied.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        distc = abs(nx - cx) + abs(ny - cy)
        score -= distc * 0.001
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]