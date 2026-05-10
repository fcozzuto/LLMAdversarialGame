def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def adj_obst(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    return 1
        return 0

    best = None
    best_score = None
    for p in resources:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        x, y = int(p[0]), int(p[1])
        if not inb(x, y) or (x, y) in obs:
            continue
        myd = cheb(sx, sy, x, y)
        opd = cheb(ox, oy, x, y)
        score = myd + 0.7 * adj_obst(x, y) - 0.45 * opd
        if best_score is None or score < best_score or (score == best_score and (x, y) < best):
            best_score = score
            best = (x, y)

    tx, ty = best if best is not None else (sx, sy)
    if sx == tx and sy == ty:
        return [0, 0]

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_mscore = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox + (0 if ox == ox else 0), oy + (0 if oy == oy else 0), tx, ty)  # deterministic no-op
        # tie-break also discourages stepping adjacent to obstacles
        mscore = myd + 0.7 * adj_obst(nx, ny) - 0.15 * opd
        if best_mscore is None or mscore < best_mscore:
            best_mscore = mscore
            best_move = [dx, dy]

    return best_move