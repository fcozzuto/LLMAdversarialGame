def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    if unclaimed:
        tx, ty = None, None
        best = 10**18
        for x, y in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            if d < best:
                best = d
                tx, ty = x, y
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        opp_dist = abs(ox - nx) + abs(oy - ny)
        # Prefer getting closer to target; tie-break by moving away from opponent.
        score = -dist * 10 + opp_dist
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]