def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role)

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res_list.append((x, y))
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res_list.append((x, y))
    if not res_list and isinstance(observation.get("remaining_resource_count"), int):
        pass

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        if res_list:
            d = min(dist(nx, ny, rx, ry) for rx, ry in res_list)
            oppd = dist(nx, ny, ox, oy)
            val = d - (oppd * 0.05 if is_evader else -oppd * 0.05)
        else:
            oppd = dist(nx, ny, ox, oy)
            val = -oppd if is_evader else oppd

        if best_val is None or (val < best_val if not is_evader else val > best_val):
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best