def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    turns = int(observation.get("turn_index", 0))

    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        # Prefer positive race lead; then go closer; then deterministic tie using coordinates and turn.
        key = (adv, -sd, (tx + ty) * 1000 + (turns % 17))
        if best_key is None or key > best_key:
            best_key, best = key, (tx, ty)

    tx, ty = best

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    preferred = []
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    preferred.append((dx, dy))
    if dx != 0 or dy != 0:
        preferred.append((dx, 0))
        preferred.append((0, dy))

    candidates = []
    for mdx, mdy in preferred + moves:
        nx, ny = sx + mdx, sy + mdy
        if mdx in (-1, 0, 1) and mdy in (-1, 0, 1) and in_bounds(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((mdx, mdy))
    if not candidates:
        return [0, 0]

    bestm = None
    bestmk = None
    for mdx, mdy in candidates:
        nx, ny = sx + mdx, sy + mdy
        d_after = cheb(nx, ny, tx, ty)
        d_now = cheb(sx, sy, tx, ty)
        # Greedy towards target with a mild anti-oscillation bias by preferring moves that don't increase distance.
        key = (-(d_after > d_now), -d_after, mdx * 3 + mdy + ((nx + 2 * ny + turns) % 3) * 0.001)
        if bestmk is None or key > bestmk:
            bestmk, bestm = key, (mdx, mdy)

    return [int(bestm[0]), int(bestm[1])]