def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    bestv = -10**9

    res_list = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if inb(rx, ry) and (rx, ry) not in obst:
            res_list.append((rx, ry))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        if not res_list:
            vx = -(md(nx, ny, ox, oy))
            v = vx
        else:
            v = -md(nx, ny, ox, oy)
            for rx, ry in res_list:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                gain = (do - ds)
                if ds == 0:
                    gain += 5
                if ds <= 1:
                    gain += 2
                v += gain
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    dx, dy = best
    return [int(dx), int(dy)]