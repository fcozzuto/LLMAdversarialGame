def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    # Target resource where we are more likely to arrive first (chebyshev distance).
    best = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer positive advantage; then shorter self distance; then deterministic coords.
        adv = od - sd
        cand = (adv, -sd, -x, -y, x, y)
        if best is None or cand > best:
            best = cand
    tx, ty = best[4], best[5]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        # Move selection balances getting closer to target while staying away from opponent proximity.
        dist_t = cheb(nx, ny, tx, ty)
        dist_o = cheb(nx, ny, ox, oy)
        # Higher dist_o preferred (avoid being intercepted); tie-break deterministically.
        val = (-dist_t, dist_o, -abs(dx), -abs(dy), dx, dy)
        if bestm is None or val > bestm:
            bestm = val
    if bestm is None:
        return [0, 0]
    return [bestm[4], bestm[5]]