def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Move away from opponent slightly while staying legal
        best = (None, -10**18)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                margin = cheb(nx, ny, ox, oy)
                key = margin * 10 - (nx * 3 + ny)
                if key > best[1]:
                    best = ((dx, dy), key)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    # Choose resource to contest: maximize advantage in distance (opponent-self), then self closeness.
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer targets we can reach no later; but also deny fast opponent reach.
        key = ((od - sd) * 1000) - sd * 5 - (rx * 2 + ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # Pick move that improves our odds for that target; if tie, improve margin vs opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Primary: reduce our distance to target; Secondary: increase opponent disadvantage.
        val = (od - sd2) * 1000 - sd2 * 10 - (nx * 2 + ny)
        # If we don't reach the target sooner, slightly prefer distancing from opponent.
        if val == best_val:
            val += cheb(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]