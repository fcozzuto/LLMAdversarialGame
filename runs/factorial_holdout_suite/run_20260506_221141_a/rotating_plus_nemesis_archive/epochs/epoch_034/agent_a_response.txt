def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    resources_raw = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and in_bounds(x, y):
                obs.add((x, y))

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and in_bounds(x, y) and (x, y) not in obs:
                resources.append((x, y))

    if not (isinstance(sx, int) and isinstance(sy, int) and in_bounds(sx, sy)):
        return [0, 0]
    if not (isinstance(ox, int) and isinstance(oy, int) and in_bounds(ox, oy)):
        ox, oy = 0, 0

    if not resources:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a race-winning target: maximize (opp_dist - my_dist), then minimize my_dist.
    best = None
    for (tx, ty) in resources:
        md = manh(sx, sy, tx, ty)
        od = manh(ox, oy, tx, ty)
        key = (od - md, -md, tx, ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty))
    (tx, ty) = best[1]

    # Choose greedy move toward target, avoid obstacles, tie-break by staying farther from opponent.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        md = manh(nx, ny, tx, ty)
        od = manh(nx, ny, ox, oy)
        # minimize distance to target; prefer being farther from opponent; deterministic tie-break by delta order already fixed
        key = (-od, md, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]