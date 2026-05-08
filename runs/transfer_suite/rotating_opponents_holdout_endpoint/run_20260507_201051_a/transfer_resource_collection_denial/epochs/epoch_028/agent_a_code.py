def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def norm_cell(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            return (x, y) if 0 <= x < w and 0 <= y < h else None
        if isinstance(p, dict):
            pos = p.get("position", p.get("pos", p.get("location", None)))
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                x, y = int(pos[0]), int(pos[1])
                return (x, y) if 0 <= x < w and 0 <= y < h else None
        return None

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        c = norm_cell(p)
        if c is not None:
            obs.add(c)

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        c = norm_cell(r)
        if c is not None:
            res.append(c)

    if not res:
        return [0, 0]

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my_len = int(observation.get("remaining_resource_count", len(res)) or len(res))
    best = None
    best_score = -10**18
    for tx, ty in res:
        md = d((sx, sy), (tx, ty))
        od = d((ox, oy), (tx, ty))
        take = 10**6 - md
        lead = (od - md) * 1000
        score = take + lead
        if (tx, ty) in obs:
            score -= 10**9
        if score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            cand.append((dx, dy))

    if not cand:
        return [0, 0]

    bestm = None
    bestv = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        v = -d((nx, ny), (tx, ty)) * 10
        v -= d((nx, ny), (ox, oy))
        v += 1 if (nx, ny) == (tx, ty) else 0
        # Break ties deterministically by move order
        order = moves.index((dx, dy))
        v -= order * 1e-3
        if v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]