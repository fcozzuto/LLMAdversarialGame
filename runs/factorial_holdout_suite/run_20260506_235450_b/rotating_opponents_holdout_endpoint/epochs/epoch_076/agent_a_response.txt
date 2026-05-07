def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    tr = int(observation.get("remaining_resource_count", 999) or 999)
    endgame = (tr <= 2) or (int(observation.get("turns_remaining", 0) or 0) <= 6)

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        # Choose a target deterministically: best by (self distance, -opponent distance, coords)
        best_t = None
        best_td = None
        best_oppd = None
        for tx, ty in resources:
            d = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            key = (d, -od, ty, tx)
            if best_t is None or key < (best_td, -best_oppd, best_t[1], best_t[0]):
                best_t = (tx, ty)
                best_td = d
                best_oppd = od
        tx, ty = best_t
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Value: minimize time to own collection; in closer endgame, prioritize securing first.
        val = -self_d
        val += 0.15 * (opp_d - self_d)  # prefer targets opponent can't easily contest
        if endgame:
            val += 2.0 * (opp_d - self_d)
        # small deterministic tie-break to avoid oscillations
        val += 0.001 * (-(ny * w + nx))
        if val > best_val:
            best_val = val
            best = (dx if inb(sx + dx, sy + dy) else 0, dy if inb(sx + dx, sy + dy) else 0)
    return [int(best[0]), int(best[1])]