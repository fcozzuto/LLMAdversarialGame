def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx = int(sp[0]); sy = int(sp[1])
    ox = int(op[0]); oy = int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def parse_cells(lst):
        out = []
        for p in lst or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x = int(p[0]); y = int(p[1])
                if inb(x, y):
                    out.append((x, y))
        return out

    obstacles = set(parse_cells(observation.get("obstacles")))
    resources = [c for c in parse_cells(observation.get("resources")) if c not in obstacles]

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        ahead = od - sd
        # Prefer resources we can arrive at first; then shortest; then deterministic tie-break
        key = (ahead, -sd, -((tx + ty) & 1), -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = sx + dx
            ny = sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                deltas.append((dx, dy))
    deltas.append((0, 0))

    # If opponent is already closer to every target, change policy: head for the closest resource anyway
    opp_closer = True
    for cx, cy in resources:
        if cheb(ox, oy, cx, cy) >= cheb(sx, sy, cx, cy):
            opp_closer = False
            break
    if opp_closer:
        target = min(resources, key=lambda c: (cheb(sx, sy, c[0], c[1]), c[0], c[1]))
        tx, ty = target

    best_step = (0, 0)
    best_step_key = None
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Move that reduces our distance most; break ties by improving lead and avoiding overshooting parity
        key = (-nsd, (nod - nsd), -((nx + ny) & 1), dx, dy)
        if best_step_key is None or key > best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]