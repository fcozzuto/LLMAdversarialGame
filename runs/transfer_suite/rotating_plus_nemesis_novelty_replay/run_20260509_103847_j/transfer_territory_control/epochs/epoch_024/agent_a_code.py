def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if inside(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))

    unT = observation.get("unclaimed_cells") or []
    un = set()
    for p in unT:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obs:
                un.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        sc = 0

        if res:
            md = 10**9
            for rx, ry in res:
                d = dist(nx, ny, rx, ry)
                if d < md:
                    md = d
            sc += 1000 - md

        if un:
            if (nx, ny) in un:
                sc += 500
            else:
                md = 10**9
                for x, y in un:
                    d = dist(nx, ny, x, y)
                    if d < md:
                        md = d
                sc += 200 - md

        sc += dist(ox, oy, sx, sy) - dist(ox, oy, nx, ny)  # pressure by approaching opponent
        sc += -2 * dist(ox, oy, nx, ny) * (1 if observation.get("remaining_resource_count", 1) else 1)

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    dx, dy = best_move
    if not isinstance(dx, int) or not isinstance(dy, int):
        dx, dy = 0, 0
    if dx < -1:
        dx = -1
    if dx > 1:
        dx = 1
    if dy < -1:
        dy = -1
    if dy > 1:
        dy = 1
    return [dx, dy]