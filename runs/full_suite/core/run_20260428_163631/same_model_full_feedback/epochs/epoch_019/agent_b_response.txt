def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target we can reach no slower than opponent; otherwise pick best "race value"
    if resources:
        best = None
        bestv = None
        for (tx, ty) in resources:
            md = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # primary: reach at same/earlier; secondary: maximize (od-md); tertiary: tie-breaker by coords
            race = (od - md)
            lead = 1 if md <= od else 0
            key = (lead, race, -tx, -ty)
            if best is None or key > bestv:
                bestv = key
                best = (tx, ty)
        tx, ty = best
    else:
        # No visible resources: go to a deterministic "influence" point (center-ish)
        tx = w // 2 if sx < w // 2 else (w // 2 - 1 if w // 2 > 0 else 0)
        ty = h // 2 if sy < h // 2 else (h // 2 - 1 if h // 2 > 0 else 0)

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer reducing our distance while trying to make us "ahead" in the race to target
        score = (od - myd, -myd)
        # Secondary: if can capture immediately (standing on a resource), always take it
        if resources and (nx, ny) in set(resources):
            score = (10**9, 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]