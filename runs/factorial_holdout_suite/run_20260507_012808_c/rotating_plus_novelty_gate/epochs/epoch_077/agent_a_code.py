def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    best_res = None
    best_key = None
    best_opp = None
    best_opp_d = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        if best_opp is None or do < best_opp_d:
            best_opp, best_opp_d = (rx, ry), do
        if ds <= do:
            key = (ds - do, ds, rx, ry)  # prioritize stealable/closer
            if best_key is None or key < best_key:
                best_key, best_res = key, (rx, ry)

    target = best_res if best_res is not None else best_opp
    tx, ty = target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_to_o = man(nx, ny, ox, oy)
        score = -d_to_t + 0.05 * d_to_o  # keep approach while slightly staying away
        if score > best_score:
            best_score, best_move = score, (dx, dy)

    dx, dy = best_move
    if dx == 0 and dy == 0:
        # if all moves blocked, try toward target ignoring obstacle (engine will clamp)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [int(dx), int(dy)]