def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Rank resources by who is closer to them right now (advantage for us).
    ranked = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        ranked.append((opd - myd, -opd, -myd, rx, ry))
    if not ranked:
        return [0, 0]
    ranked.sort()
    candidates = [(t[3], t[4]) for t in ranked[:3]]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # For this move, choose the resource that maximizes our immediate advantage next turn.
        move_best = None
        for rx, ry in candidates:
            my_next = man(nx, ny, rx, ry)
            opp_now = man(ox, oy, rx, ry)
            adv_next = opp_now - my_next
            key = (adv_next, -my_next, -(rx * 97 + ry * 53), rx, ry)
            if move_best is None or key > move_best[0]:
                move_best = (key, (rx, ry))
        if move_best is None:
            continue
        mk = move_best[0]
        cur_key = (mk[0], mk[1], mk[2], dx, dy)
        if best_key is None or cur_key > best_key:
            best_key = cur_key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]