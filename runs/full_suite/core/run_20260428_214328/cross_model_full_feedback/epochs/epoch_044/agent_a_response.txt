def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and not (nx == ox and ny == oy):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    t = int(observation.get("turn_index", 0) or 0)

    def pick_target():
        if not resources:
            return (w // 2, h // 2)
        if t % 2 == 0:
            best = None; bd = None
            for rx, ry in resources:
                d = cheb(sx, sy, rx, ry)
                if bd is None or d < bd:
                    bd = d; best = (rx, ry)
            return best
        else:
            best = None; bd = None
            for rx, ry in resources:
                d = cheb(ox, oy, rx, ry)
                if bd is None or d < bd:
                    bd = d; best = (rx, ry)
            return best

    tx, ty = pick_target()

    best = None
    best_val = None
    for dx, dy, nx, ny in candidates:
        d_res = cheb(nx, ny, tx, ty)

        if resources:
            # Encourage moving into resource "frontier" rather than only chasing one point
            d_any = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d_any is None or d < d_any:
                    d_any = d
        else:
            d_any = cheb(nx, ny, w // 2, h // 2)

        d_opp = cheb(nx, ny, ox, oy)
        # Lower is better: primary reduce distance to target; secondary contest position; tertiary keep resources nearby
        val = d_res * 10.0 - d_opp * 1.0 + d_any * 0.25

        key = (val, dx, dy)
        if best_val is None or key < best_val:
            best_val = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]