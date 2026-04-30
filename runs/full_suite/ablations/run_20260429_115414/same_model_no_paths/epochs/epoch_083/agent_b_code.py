def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Deterministic safety: keep distance from opponent while staying in bounds
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            sep = cheb(nx, ny, ox, oy)
            edge = (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1)
            score = sep + (1 if edge else 0)
            if score > best[1]:
                best = ((dx, dy), score)
        return [best[0][0], best[0][1]] if best[0] else [0, 0]

    # Pick the resource where we are relatively closer than opponent (with tie-breaks).
    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        # Strongly favor being closer; slightly prefer nearer absolute distance.
        val = (d2 - d1) * 100 - d1
        # Discourage targets that are immediate for opponent but not for us.
        if d2 <= 1 and d1 > 1:
            val -= 50
        if val > best_val or (val == best_val and (d1 < cheb(sx, sy, best_r[0], best_r[1]) if best_r else True)):
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r
    # If contested (opponent close), prioritize blocking by moving to maximize separation while still trending to target.
    my_d = cheb(sx, sy, tx, ty)
    op_d = cheb(ox, oy, tx, ty)
    contested = op_d <= my_d + 1

    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        new_my = cheb(nx, ny, tx, ty)
        new_sep = cheb(nx, ny, ox, oy)
        # Main: decrease distance to target; Secondary: if contested, increase separation.
        s1 = -new_my * 10
        s2 = (new_sep * 2 if contested else new_sep * 0.2)
        # Slight preference to reduce opponent's distance to our position when not contested.
        opp_to_us = cheb(ox, oy, nx, ny)
        s3 = (-opp_to_us * 0.3)
        score = s1 + s2 + s3
        if score > best_s:
            best_s = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]