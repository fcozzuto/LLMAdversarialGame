def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs_set = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs_set.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs_set:
                resources.append((x, y))
    if not resources:
        resources = []

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs_set:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = legal[0]
    best_val = -10**18
    has_res = len(resources) > 0
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_opp = man(nx, ny, ox, oy)
        if has_res:
            d_res = min(man(nx, ny, rx, ry) for rx, ry in resources)
            val = (d_opp * 2 - d_res)
        else:
            val = d_opp
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]