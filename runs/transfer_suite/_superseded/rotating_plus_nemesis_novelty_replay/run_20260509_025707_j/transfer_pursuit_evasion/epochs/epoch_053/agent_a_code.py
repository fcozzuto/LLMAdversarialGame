def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources") or []
    rem = observation.get("remaining_resource_count")
    if resources and isinstance(resources[0], (list, tuple)) and len(resources[0]) >= 2:
        res = []
        for r in resources:
            if len(r) >= 2:
                x, y = int(r[0]), int(r[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    res.append((x, y))
    else:
        res = []

    role = (observation.get("self_role") or "").lower()
    want_kill = ("attacker" in role) or ("chaser" in role) or ("hunter" in role)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if res:
            dres = min(md(nx, ny, rx, ry) for rx, ry in res)
            val = 1000 - dres
        else:
            dopp = md(nx, ny, ox, oy)
            val = ddown = d_md = dopp if not want_kill else -dopp
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]
    return [int(best[0]), int(best[1])]