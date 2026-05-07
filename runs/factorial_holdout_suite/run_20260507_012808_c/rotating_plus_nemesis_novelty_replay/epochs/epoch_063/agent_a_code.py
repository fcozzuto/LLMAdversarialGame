def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    ti = int(observation.get("turn_index", 0) or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    best_tx, best_ty = None, None
    best_key = None
    for tx, ty in resources:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        closer = do - ds  # positive means we're closer
        # Prefer resources we can win; otherwise still prefer nearest but slightly penalize likely opponent priority
        key = (-(closer), ds, (tx + 3 * ty + ti) % 10)
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = tx, ty

    tx, ty = best_tx, best_ty
    if (tx, ty) is None:
        return [0, 0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ds_next = man(nx, ny, tx, ty)
        do_now = man(ox, oy, tx, ty)
        # Encourage getting strictly closer; discourage moving toward a resource the opponent is already winning
        win_margin = do_now - ds_next
        score = (-win_margin, ds_next, (nx - nx*ny + ti) % 7)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]