def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in sr) or ("runner" in sr)
    if ("pursuer" in sr) or ("chaser" in sr) or ("hunter" in sr):
        if "evader" in sr:
            is_evader = True
        else:
            is_evader = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def blocked(x, y):
        return not (0 <= x < w and 0 <= y < h) or (x, y) in obstacles

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res_list.append((x, y))

    if res_list:
        dists = []
        for x, y in res_list:
            d = abs(x - sx) + abs(y - sy)
            dists.append((d, x, y))
        if is_evader:
            dists.sort(key=lambda t: (-t[0], t[1], t[2]))
        else:
            dists.sort(key=lambda t: (t[0], t[1], t[2]))
        tx, ty = dists[0][1], dists[0][2]
    else:
        if is_evader:
            tx, ty = 2 * sx - ox, 2 * sy - oy
        else:
            tx, ty = ox, oy
        tx = max(0, min(w - 1, tx))
        ty = max(0, min(h - 1, ty))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        score = dist if not is_evader else -dist
        cand = (score, nx, ny, dx, dy)
        if best is None or cand < best if not is_evader else cand[0] > best[0] or (cand[0] == best[0] and cand[1:3] < best[1:3]):
            best = cand

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]

    return [int(best[3]), int(best[4])]