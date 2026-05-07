def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    turns = int(observation.get("turns_remaining", 0) or 0)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0: d1 = -d1
        d2 = y1 - y2
        if d2 < 0: d2 = -d2
        return d1 if d1 >= d2 else d2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_cell = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer cells we can reach no later than opponent, then closer; penalize far targets.
        reach_pen = 0
        if sd > turns:
            # If we can't reach in time, strongly deprioritize but still consider if few options.
            reach_pen = 1000 + (sd - turns)
        key = ((od - sd), -sd - reach_pen, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (tx, ty)

    tx, ty = best_cell
    # Choose move that improves advantage and reduces distance to target, while avoiding obstacles.
    best_move = [0, 0]
    best_mv_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        adv = nod - nsd
        # Small deterministic bias toward staying closer to center-ish: lower max distance to avoid corners late.
        center_bias = max(abs(nx - (w // 2)), abs(ny - (h // 2)))
        mv_key = (adv, -nsd, -center_bias, dx, dy)
        if best_mv_key is None or mv_key > best_mv_key:
            best_mv_key = mv_key
            best_move = [dx, dy]

    return best_move