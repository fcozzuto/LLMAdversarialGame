def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    un_list = observation.get("unclaimed_cells") or []
    tgt_list = un_list if un_list else (observation.get("resources") or [])

    tgts = []
    for p in tgt_list:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            tgts.append((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obs

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if tgts:
            d_t = min(dist(nx, ny, tx, ty) for tx, ty in tgts)
        else:
            d_t = 0
        d_o = dist(nx, ny, ox, oy)
        score = (d_t == 0) * 100000 + (-d_t) + (0.05 * d_o)
        key = (score, -d_o, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        for dx, dy in [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best[1]