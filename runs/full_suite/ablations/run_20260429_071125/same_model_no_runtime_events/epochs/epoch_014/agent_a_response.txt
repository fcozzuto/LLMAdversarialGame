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
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best = None
    best_adv = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = (od - sd) * 10 - sd
        if best_adv is None or adv > best_adv:
            best_adv = adv
            best = (rx, ry)

    rx, ry = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer taking/approaching the target; also avoid giving opponent an immediate path by staying away
        val = -d_self * 20 + d_opp * 1
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]