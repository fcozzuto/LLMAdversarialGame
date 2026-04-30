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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not valid(sx, sy):
        for mx, my in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            if valid(mx, my):
                sx, sy = mx, my
                break

    # Pick a contested target: maximize (opponent advantage we deny) = (opp_dist - our_dist)
    best = None
    best_sc = None
    for (rx, ry) in resources:
        if not valid(rx, ry):
            continue
        d_ours = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        corner_bias = 0
        # Prefer resources that keep us moving "forward" from our corner
        if sx <= 1 and sy <= 1:
            corner_bias = (rx + ry)
        else:
            corner_bias = ((w - 1 - rx) + (h - 1 - ry))
        sc = (d_opp - d_ours) * 10 - d_ours - 0.01 * corner_bias
        if best_sc is None or sc > best_sc or (sc == best_sc and (rx, ry) < best):
            best_sc = sc
            best = (rx, ry)

    tx, ty = best if best is not None else resources[0]
    best_move = [0, 0]
    best_val = None

    # Greedy step toward target with obstacle-aware tie-breaking
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue_ok = True
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # prefer reducing chebyshev distance; tie-break by keeping direction (align with target)
            cur = cheb(nx, ny, tx, ty)
            align = abs((nx - tx)) + abs((ny - ty))
            # diagonal slight bonus
            diag_bonus = 0.2 if dx != 0 and dy != 0 else 0.0
            val = (-cur, -diag_bonus, align, dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move