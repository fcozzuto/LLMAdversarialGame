def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) if p is not None)
    resources = observation.get("resources", None)
    if resources is None:
        resources = []
    if isinstance(resources, dict):
        resources = list(resources.values())

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def rpos(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict):
            if "position" in r:
                p = r["position"]
                return int(p[0]), int(p[1])
            for k in ("x", "y"):
                if k not in r:
                    break
            else:
                return int(r["x"]), int(r["y"])
        return None

    res_list = []
    for r in resources:
        p = rpos(r)
        if p is not None:
            rx, ry = p
            if inb(rx, ry) and (rx, ry) not in obstacles:
                res_list.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res_list:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = -cheb(nx, ny, tx, ty) + 0.25 * cheb(nx, ny, ox, oy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    closest = None
    bestd = None
    for rx, ry in res_list:
        d = cheb(sx, sy, rx, ry)
        if bestd is None or d < bestd:
            bestd, closest = d, (rx, ry)

    tx, ty = closest
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dr = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        score = -dr + 0.25 * do
        if best is None or score > best[0] or (score == best[0] and abs(dx) + abs(dy) < best[1]):
            best = (score, abs(dx) + abs(dy), dx, dy)

    if best is None:
        return [0, 0]
    return [best[2], best[3]]