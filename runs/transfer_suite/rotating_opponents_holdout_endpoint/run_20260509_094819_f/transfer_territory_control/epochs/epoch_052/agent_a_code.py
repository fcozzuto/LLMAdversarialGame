def choose_move(observation):
    def to_pair(v):
        if v is None:
            return None
        try:
            return int(v[0]), int(v[1])
        except Exception:
            return None

    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = to_pair(observation.get("self_position") or (0, 0))
    op = to_pair(observation.get("opponent_position") or (0, 0))
    if sp is None:
        sp = (0, 0)
    sx, sy = sp

    obstacles = set()
    for p in observation.get("obstacles") or []:
        q = to_pair(p)
        if q:
            obstacles.add(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    targets = []
    if unclaimed:
        targets = [to_pair(p) for p in unclaimed]
    elif resources:
        targets = [to_pair(p) for p in resources]
    elif op is not None:
        targets = [op]
    else:
        targets = [(sx, sy)]

    targets = [t for t in targets if t is not None]

    def best_dist2(x, y):
        best = None
        for tx, ty in targets:
            d = (x - tx) * (x - tx) + (y - ty) * (y - ty)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = -best_dist2(nx, ny)
        sp_terr = observation.get("self_territory") or []
        if sp_terr:
            for p in sp_terr:
                q = to_pair(p)
                if q == (nx, ny):
                    score += 2
                    break
        opp_pos = op
        if opp_pos is not None:
            ox, oy = opp_pos
            if abs(nx - ox) + abs(ny - oy) <= 1:
                score += 1
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    if not (0 <= sx < w and 0 <= sy < h) or (sx, sy) in obstacles:
        return [0, 0]
    if best_score == -10**18:
        return [0, 0]
    return best_move