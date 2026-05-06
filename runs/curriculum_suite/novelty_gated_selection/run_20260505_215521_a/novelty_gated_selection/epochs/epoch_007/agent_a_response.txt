def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    def man(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: prioritize resources we can contest (we closer than opponent),
    # and avoid easily-taken edge resources when opponent is nearer.
    best_t = None
    best_k = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        edge = 1 if tx in (0, w - 1) or ty in (0, h - 1) else 0
        # Prefer: (od - sd) high; penalize edge when opponent is closer.
        k = (-(od - sd), edge * (1 if od < sd else 0), sd, tx, ty)
        if best_k is None or k < best_k:
            best_k = k
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t

    # Move evaluation: avoid obstacles, aim to reduce our distance to target,
    # but also increase opponent distance to same target.
    bestm = (0, 0)
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        edge = 1 if tx in (0, w - 1) or ty in (0, h - 1) else 0
        # If target is an edge, slightly favor moves that keep us away from opponent's edge pressure:
        # approximate by preferring higher distance from opponent.
        self_to_opp = man(nx, ny, ox, oy)
        v = (-(sd2) + 0.25 * self_to_opp - 0.1 * edge * sd2, -od2, -sd2, dx, dy)
        if bestv is None or v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]