def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    cx, cy = w // 2, h // 2

    # Pick resource where we are (deterministically) relatively advantaged.
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = ds - do  # negative means we are closer
        # prefer: we are closer; then shorter distance; then closer to center (minor)
        key = (abs(adv), adv, ds, cheb(rx, ry, cx, cy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    if not best_res:
        # No resources: deterministically move to keep distance from opponent while centralizing.
        moves = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((-(cheb(nx, ny, ox, oy)) + 0.05 * (w - cheb(nx, ny, cx, cy)), nx, ny, dx, dy))
        if not moves:
            return [0, 0]
        moves.sort()
        return [moves[0][3], moves[0][4]]

    rx, ry = best_res

    # Score candidate moves: progress to target, stay away from opponent, avoid dead movement.
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_t = cheb(nx, ny, rx, ry)
        d_o = cheb(nx, ny, ox, oy)
        # prefer grabbing target sooner; if tie, prefer staying further from opponent; then central bias; then deterministic move order
        score = (-d_t, d_o, -cheb(nx, ny, cx, cy), dx, dy)
        cand.append((score, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    return [cand[0][1], cand[0][2]]