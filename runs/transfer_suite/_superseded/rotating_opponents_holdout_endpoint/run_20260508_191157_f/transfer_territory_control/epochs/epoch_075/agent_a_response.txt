def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    opp_terr = []
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                opp_terr.append((x, y))

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    candidates = unclaimed if unclaimed else opp_terr
    if not candidates:
        return [0, 0]

    best = None
    bestv = None
    opp_in = set(opp_terr)
    for tx, ty in candidates:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        is_opp = 1 if (tx, ty) in opp_in else 0
        v = (-ds) + 0.15 * do + 0.6 * is_opp
        if best is None or v > bestv or (v == bestv and (tx, ty) < best):
            bestv = v
            best = (tx, ty)

    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer reducing distance; lightly prefer approaching target while not walking into opponent too directly.
        sdist = md(nx, ny, tx, ty)
        odist = md(nx, ny, ox, oy)
        score = (-sdist) + 0.05 * odist
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_step):
            best_score = score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]