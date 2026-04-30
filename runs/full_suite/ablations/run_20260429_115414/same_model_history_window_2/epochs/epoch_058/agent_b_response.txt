def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if resources:
        best = None
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            ds = 10**9
            do = 10**9
            for rx, ry in resources:
                ds0 = man(nx, ny, rx, ry)
                if ds0 < ds: ds = ds0
                do0 = man(ox, oy, rx, ry)
                if do0 < do: do = do0
            # prefer getting closer now; if tie, prefer making opponent farther
            # tiny deterministic tie-break via move order by using val adjustments
            val = -ds + (do * 0.35)
            if best is None or val > best_val:
                best_val = val
                best = (dx, dy)
        if best is not None:
            return [int(best[0]), int(best[1])]

    # No resources (or all blocked): move toward farthest corner from opponent
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda p: (man(ox, oy, p[0], p[1]), -p[0], -p[1]))
    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dcur = man(nx, ny, tx, ty)
        # also avoid getting closer to opponent
        dopp = man(nx, ny, ox, oy)
        val = -dcur + 0.15 * dopp
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]