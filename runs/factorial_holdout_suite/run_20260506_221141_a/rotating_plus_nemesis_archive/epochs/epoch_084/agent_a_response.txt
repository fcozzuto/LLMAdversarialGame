def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_score = -10**18

    # If no visible resources, just head toward opponent corner to stay engaged.
    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Evaluate each possible next move by looking at lead margin vs opponent for remaining resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cur = 0
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            # Big weight on being earlier than opponent; also reward closeness for tie situations.
            lead = opp_d - self_d
            s = lead * 200 - self_d * 3
            if (nx, ny) == (rx, ry):
                s += 1000000
            cur += s

        # Add a small preference for moves that reduce distance to the single best target.
        # (Keeps behavior stable/decisive without heavy search.)
        min_self = 10**9
        min_margin = -10**9
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            if self_d < min_self:
                min_self = self_d
            margin = opp_d - self_d
            if margin > min_margin:
                min_margin = margin
        cur += min_margin * 20 - min_self

        if cur > best_score:
            best_score = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]