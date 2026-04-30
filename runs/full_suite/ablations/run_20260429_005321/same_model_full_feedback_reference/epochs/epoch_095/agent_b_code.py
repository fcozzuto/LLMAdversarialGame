def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target where we have the biggest distance advantage over the opponent.
    best_t = None
    best_adv = None
    for tx, ty in resources:
        da = cheb(sx, sy, tx, ty)
        db = cheb(ox, oy, tx, ty)
        adv = (db - da)  # positive means we're closer
        key = (adv, -da, tx, ty)
        if best_t is None or key > best_adv:
            best_t = (tx, ty)
            best_adv = key
    if best_t is None:
        best_t = (w // 2, h // 2)

    tx, ty = best_t

    # Evaluate next move: go to target, keep opponent farther, and avoid stepping onto dead-end-ish cells.
    # Deterministic tie-breaking by fixed dir order.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        cur_to_target = cheb(sx, sy, tx, ty)
        cur_to_opp = cheb(sx, sy, ox, oy)

        # Encourage reducing target distance while not letting opponent get too close.
        score = (-myd * 5) + ((opd - cur_to_opp) * 1) + (-(myd - cur_to_target) * 2)
        # If we're equal on target distance, prefer moving away from opponent.
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]