def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role_s = str(observation.get("self_role") or "").lower()
    is_evader = any(k in role_s for k in ("evad", "run", "away", "escape", "runner"))
    is_pursuer = ("purs" in role_s) or ("hunt" in role_s) or ("chase" in role_s)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = None

    def md_to_block(x, y):
        md = 10**9
        for bx, by in blocked:
            d = abs(bx - x) + abs(by - y)
            if d < md:
                md = d
        return md if blocked else 99

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        md = md_to_block(nx, ny)
        val = (-dist if is_pursuer else dist) + (md * 0.01)
        if bestv is None or val > bestv or (val == bestv and (dx, dy) < best):
            bestv = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]