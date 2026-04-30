def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obst = observation.get("obstacles", []) or []
    occ = set()
    for p in obst:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            occ.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    best = None
    if resources:
        for r in resources:
            if isinstance(r, dict):
                if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                    rx, ry = r["position"][0], r["position"][1]
                elif "x" in r and "y" in r:
                    rx, ry = r["x"], r["y"]
                else:
                    continue
            elif isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
            else:
                continue
            rx, ry = int(rx), int(ry)
            d = cd(sx, sy, rx, ry)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
    if best is not None:
        tx, ty = best[1]
    else:
        tx, ty = (w // 2), (h // 2)

    moves = []
    for mx, my in ((0, -1), (1, 0), (0, 1), (-1, 0), (-1, -1), (1, -1), (1, 1), (-1, 1), (0, 0)):
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        if mx == 0 and my == 0:
            penalty = 1
        else:
            penalty = 0
        cost = cd(nx, ny, tx, ty) + 0.08 * cd(nx, ny, ox, oy) + 0.02 * penalty
        moves.append((cost, mx, my))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], t[1], t[2]))
    return [moves[0][1], moves[0][2]]