def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry):
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        # Prefer resources where we have a clear race advantage; still allow small negatives if nothing else.
        lane_pen = 0
        if abs(ry - oy) <= 1:
            lane_pen = 2
        key = (adv - lane_pen, -sd, -abs(rx - sx), -abs(ry - sy), -rx - ry)
        if best is None or key > best[0]:
            best = (key, rx, ry, sd, od)

    if best is None:
        return [0, 0]

    _, tx, ty, sd0, od0 = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_next = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        adv_next = nod - nsd
        # If opponent is closer, avoid letting our move make it worse than staying still.
        bad = 0
        if od0 < sd0 and nsd > sd0 + 0:
            bad = 3
        key = (adv_next - bad, -nsd, -abs(tx - nx), -abs(ty - ny), dx, dy)
        if best_next is None or key > best_next[0]:
            best_next = (key, dx, dy)

    if best_next is None:
        return [0, 0]
    return [int(best_next[1]), int(best_next[2])]