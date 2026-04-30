def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles:
        return [0, 0]

    has_res = len(resources) > 0
    if not has_res:
        tx, ty = ox, oy
    else:
        tx, ty = resources[0][0], resources[0][1]

    def best_target(x, y):
        if not resources:
            return ox, oy
        md = None
        bt = resources[0]
        for rx, ry in resources:
            d = abs(rx - x)
            dd = abs(ry - y)
            dist = d if d > dd else dd  # Chebyshev
            if md is None or dist < md:
                md = dist
                bt = (rx, ry)
        return bt

    tx, ty = best_target(sx, sy)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if resources and (nx, ny) in resources:
            score_key = (-10, 0, dx, dy)
            if best is None or score_key < best[0]:
                best = (score_key, dx, dy)
            continue
        dist = abs(tx - nx)
        dd = abs(ty - ny)
        cheb = dist if dist > dd else dd
        opp_adj = max(abs(ox - nx), abs(oy - ny))
        # Prefer closer to target; avoid immediate adjacency to opponent a bit; deterministic tie-break.
        score_key = (cheb, opp_adj * 0.01, dx, dy)
        if best is None or score_key < best[0]:
            best = (score_key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]