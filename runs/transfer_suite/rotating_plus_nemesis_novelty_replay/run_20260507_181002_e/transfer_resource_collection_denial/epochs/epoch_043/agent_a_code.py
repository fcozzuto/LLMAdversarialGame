def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def p2(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        if isinstance(v, dict):
            t = v.get("position", v.get("pos", None))
            if isinstance(t, (list, tuple)) and len(t) >= 2:
                return (int(t[0]), int(t[1]))
        return None

    sp = p2(observation.get("self_position", None))
    op = p2(observation.get("opponent_position", None))
    if sp is None:
        sp = (0, 0)
    if op is None:
        op = sp
    sx, sy = sp
    ox, oy = op

    obstacles = set()
    for ob in observation.get("obstacles", []) or []:
        q = p2(ob)
        if q is None:
            continue
        x, y = q
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        q = p2(r)
        if q is None:
            continue
        x, y = q
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    best = None
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dres = None
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if dres is None or d < dres:
                dres = d
        if dres is None:
            dres = 0
        dob_now = md(sx, sy, ox, oy)
        dob_next = md(nx, ny, ox, oy)
        score = -dres + 0.15 * (dob_next - dob_now)  # prefer decreasing opponent distance
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]