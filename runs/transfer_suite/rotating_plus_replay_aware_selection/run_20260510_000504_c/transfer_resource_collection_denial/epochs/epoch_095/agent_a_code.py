def choose_move(observation):
    def get_xy(obj):
        if isinstance(obj, (list, tuple)) and len(obj) >= 2:
            return int(obj[0]), int(obj[1])
        if isinstance(obj, dict):
            if "position" in obj and isinstance(obj["position"], (list, tuple)) and len(obj["position"]) >= 2:
                return int(obj["position"][0]), int(obj["position"][1])
            if "x" in obj and "y" in obj:
                return int(obj["x"]), int(obj["y"])
        return 0, 0

    def parse_pts(items):
        out = []
        if not items:
            return out
        for it in items:
            if isinstance(it, (list, tuple)) and len(it) >= 2:
                out.append((int(it[0]), int(it[1])))
            elif isinstance(it, dict):
                x, y = get_xy(it)
                out.append((x, y))
        return out

    sx, sy = get_xy(observation.get("self_position"))
    ox, oy = get_xy(observation.get("opponent_position"))
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    resources = parse_pts(observation.get("resources"))
    obstacles = set(parse_pts(observation.get("obstacles")))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    bd = None
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        # Tie-break: prefer resource not closer to opponent
        score = (d, cheb(ox, oy, rx, ry))
        if bd is None or score < bd:
            bd = score
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy)))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (t[2], t[3]))
    dx, dy = candidates[0][0], candidates[0][1]
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]