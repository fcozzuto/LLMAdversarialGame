def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        best_adv = None
        best_my = None
        # Prefer resources where we are closer than opponent; then race for nearest.
        for x, y in resources:
            d_me = man(sx, sy, x, y)
            d_op = man(ox, oy, x, y)
            adv = d_op - d_me  # bigger => more winning
            if best is None or adv > best_adv or (adv == best_adv and d_me < best_my):
                best = (x, y)
                best_adv = adv
                best_my = d_me
        tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dx_t = 0 if tx == sx else (1 if tx > sx else -1)
    dy_t = 0 if ty == sy else (1 if ty > sy else -1)

    # Choose best single-step move: minimize distance to target; avoid obstacles deterministically.
    best_step = [dx_t, dy_t]
    best_dist = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # Slightly prefer moves that also reduce opponent's distance to the same target (indirect contest).
        d_op = man(nx, ny, ox, oy)
        key = (d, d_op)
        if d < best_dist or (d == best_dist and [dx, dy] < best_step):
            best_dist = d
            best_step = [dx, dy]

    return [int(best_step[0]), int(best_step[1])]