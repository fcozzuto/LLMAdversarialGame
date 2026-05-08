def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources = observation.get("resources") or []
    if resources and isinstance(resources[0], dict):
        res_list = [(int(r.get("x", 0)), int(r.get("y", 0))) for r in resources if r is not None]
    else:
        res_list = []
        for r in resources:
            if r is None:
                continue
            if isinstance(r, dict):
                res_list.append((int(r.get("x", 0)), int(r.get("y", 0))))
            else:
                res_list.append((int(r[0]), int(r[1])))

    def ok(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    if res_list:
        best_rx, best_ry = None, None
        best_adv = None
        for rx, ry in res_list:
            if not inside(rx, ry) or (rx, ry) in obstacles:
                continue
            ds = dist2(sx, sy, rx, ry)
            do = dist2(ox, oy, rx, ry)
            adv = ds - do  # smaller ds relative to do is better for us
            if best_adv is None or adv < best_adv:
                best_adv, best_rx, best_ry = adv, rx, ry
    else:
        best_rx, best_ry = ox, oy  # fallback: just manage distance

    pursue = True
    if best_rx is not None:
        pursue = dist2(sx, sy, best_rx, best_ry) <= dist2(ox, oy, best_rx, best_ry)
    else:
        pursue = True

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        if pursue:
            d_res = dist2(nx, ny, best_rx, best_ry) if best_rx is not None else 0
            score = (-(d_res)) * 10 - d_opp
        else:
            score = d_opp - dist2(nx, ny, best_rx, best_ry) * 0.5 if best_rx is not None else d_opp
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]