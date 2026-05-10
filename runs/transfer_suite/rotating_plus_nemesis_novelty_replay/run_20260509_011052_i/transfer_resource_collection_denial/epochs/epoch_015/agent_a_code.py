def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_pair(p):
        try:
            return int(p[0]), int(p[1])
        except Exception:
            return None

    obs = set()
    for t in observation.get("obstacles", []) or []:
        q = to_pair(t)
        if q is not None:
            obs.add(q)

    resources = []
    for t in observation.get("resources", []) or []:
        q = to_pair(t)
        if q is not None:
            resources.append(q)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)  # capture advantage: larger od-sd first
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_md = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        md = dist(nx, ny, tx, ty)
        key = (md, -abs(dx), -abs(dy), dx, dy)  # deterministic tie-break
        if best_md is None or key < best_md:
            best_md = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]