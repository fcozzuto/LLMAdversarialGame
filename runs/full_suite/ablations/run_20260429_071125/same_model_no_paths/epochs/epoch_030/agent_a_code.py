def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not ok(sx, sy):
        for dx, dy in [(0,0),(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_t = None
        best_adv = None
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            key = (adv, -sd)
            if best_t is None or key > best_key:
                best_t = (rx, ry)
                best_adv = adv
                best_key = key
        tx, ty = best_t

        best_move = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            sd2 = dist(nx, ny, tx, ty)
            od2 = dist(ox, oy, tx, ty)
            # Prefer progress to target; if tie, prefer moves that make opponent worse (via closer-to-target advantage)
            val = (-(sd2), (od2 - sd2), -abs(nx - tx) - abs(ny - ty))
            if best_move is None or val > best_val:
                best_move = (dx, dy)
                best_val = val
        return [best_move[0], best_move[1]]

    # No resources visible: drift toward center while keeping distance from opponent
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dcent = dist(nx, ny, cx, cy)
        dop = dist(nx, ny, ox, oy)
        val = (-dcent, dop)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]