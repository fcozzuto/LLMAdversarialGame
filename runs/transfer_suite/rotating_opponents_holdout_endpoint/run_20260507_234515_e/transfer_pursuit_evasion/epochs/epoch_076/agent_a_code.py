def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sp[0]), int(sp[1]), int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    resources = observation.get("resources", []) or []
    rlist = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rlist.append((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    env = str(observation.get("environment_name", "") or "").lower()
    is_evader = ("evader" in self_role) or ("evasion" in env) or ("evader" in env)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in oset

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        md = 10**9
        for rx, ry in rlist:
            d = abs(rx - nx) + abs(ry - ny)
            if d < md:
                md = d
        if not rlist:
            md = 0

        dop = abs(ox - nx) + abs(oy - ny)
        v = 0
        if rlist:
            v += 1000 - md
        if is_evader:
            v += dop
        else:
            v -= dop

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]