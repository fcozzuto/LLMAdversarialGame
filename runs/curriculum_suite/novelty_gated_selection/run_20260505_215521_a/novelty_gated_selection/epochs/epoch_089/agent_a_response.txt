def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_target(tx, ty):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer resources where we are closer or where opponent is far.
        # Small bonus for being near and penalty if opponent is closer by a margin.
        return (ds <= do) * (40 - ds) + (ds - do) * (-2) + (-(cheb(tx, ty, w - 1, h - 1)) * 0.01)

    if not resources:
        # No visible resources: move away from opponent while staying in-bounds and not on obstacles.
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best[1]:
                best = ((dx, dy), d)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    # Pick target using deterministic tie-breaking on (score, dx_to_target, dy_to_target, target_x, target_y)
    best_t = None
    best_key = None
    for (tx, ty) in resources:
        if not inb(tx, ty) or (tx, ty) in obst:
            continue
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        key = (score_target(tx, ty), -ds, -(do - ds), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Choose next step: minimize distance to target, avoid obstacles; tie-break by distancing opponent.
    best_m = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        dt = cheb(nx, ny, tx, ty)
        dpo = cheb(nx, ny, ox, oy)
        val = (-dt, dpo, -abs((tx - nx)) - abs((ty - ny)), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]