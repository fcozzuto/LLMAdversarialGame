def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            key = (cheb(nx, ny, cx, cy), abs((ox - nx)) + abs((oy - ny)))
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Deny: if opponent is very close to a resource, go for it.
    deny = None
    for rx, ry in resources:
        dpo = cheb(ox, oy, rx, ry)
        if dpo <= 2:
            if deny is None or (dpo, cheb(sx, sy, rx, ry)) < deny:
                deny = (dpo, cheb(sx, sy, rx, ry), rx, ry)

    def target_score(rx, ry):
        dself = cheb(sx, sy, rx, ry)
        dopp = cheb(ox, oy, rx, ry)
        # Prefer resources where we are relatively closer than the opponent.
        return (dopp - dself, -dself, rx, ry)

    if deny is not None:
        _, _, tx, ty = deny
    else:
        best_res = None
        for rx, ry in resources:
            sc = target_score(rx, ry)
            if best_res is None or sc > best_res:
                best_res = sc
        tx, ty = best_res[2], best_res[3]

    best_key = None
    best_move = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to_target = cheb(nx, ny, tx, ty)
        d_from_opp = cheb(nx, ny, ox, oy)
        # Keep some separation from opponent while homing target.
        key = (d_to_target, -d_from_opp, abs(tx - nx) + abs(ty - ny), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]