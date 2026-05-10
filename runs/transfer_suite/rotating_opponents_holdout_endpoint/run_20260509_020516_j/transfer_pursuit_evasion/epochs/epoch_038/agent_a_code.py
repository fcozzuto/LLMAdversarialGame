def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in (observation.get("obstacles") or []):
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("catcher" in role)
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    if not (is_pursuer or is_evader):
        is_pursuer = True
    if not is_pursuer:
        is_evader = True

    resources = observation.get("resources") or []
    res_pts = []
    for r in resources:
        if isinstance(r, dict):
            x, y = r.get("x"), r.get("y")
        else:
            x, y = r[0], r[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res_pts.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if res_pts:
        if is_pursuer:
            tx, ty = min(res_pts, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
            mode = "to_resource"
        else:
            tx, ty = min(res_pts, key=lambda p: (-((abs(p[0] - sx) + abs(p[1] - sy))), p[0], p[1]))
            mode = "from_resource"
    else:
        tx, ty = ox, oy
        mode = "from_opponent" if is_evader else "to_opponent"

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_to_tgt = abs(nx - tx) + abs(ny - ty)
        boundary = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        if is_pursuer:
            dist = d_to_tgt if mode == "to_resource" else d_to_opp
            score = -dist - (1 if boundary else 0)
        else:
            dist = d_to_opp if mode == "from_opponent" else d_to_tgt
            score = dist - (1 if boundary else 0)
        key = (-score, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best[1]