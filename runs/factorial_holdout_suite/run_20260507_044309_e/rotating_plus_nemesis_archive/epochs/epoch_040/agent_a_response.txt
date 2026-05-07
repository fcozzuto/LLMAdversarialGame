def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    blocked = set()
    for b in observation.get("obstacles") or []:
        try:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
        except:
            pass
    if not resources:
        return [0, 0]

    best_target = None  # (can_win_first, gap, mydist, rx, ry)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        can_first = 1 if ds <= do else 0
        gap = do - ds
        cand = (can_first, gap, ds, rx, ry)
        if best_target is None or cand > best_target:
            best_target = cand
    _, _, _, tx, ty = best_target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, None)  # (score, dist_to_target)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        my_to = cheb(nx, ny, tx, ty)
        opp_to = cheb(ox, oy, tx, ty)
        # If we are already "competing", prioritize reducing our distance; otherwise avoid giving up too much.
        ds_now = cheb(sx, sy, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        my_first = 1 if my_to <= opp_to else 0
        improve = (ds_now - my_to)
        score = (my_first, improve, -my_to, -abs(nx - tx) - abs(ny - ty))
        if best_move[0] is None or score > best_move[0]:
            best_move = (score, my_to)

    return [int(best_move[1] is None) * 0, 0] if best_move[0] is None else [best_move[0] and 0 or 0, 0]