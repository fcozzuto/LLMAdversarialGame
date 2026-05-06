def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (int(q[0]), int(q[1]))
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (int(r[0]), int(r[1]))
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    rpos_sorted = sorted(rpos, key=lambda p: (p[0], p[1]))

    def best_target():
        best = None
        for rx, ry in rpos_sorted:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach at least as fast; otherwise nearest advantage.
            key = (0 if ds <= do else 1, ds - do, ds, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry), ds, do)
        return best

    tgt = best_target()
    if not tgt:
        return [0, 0]
    (ds_adv_key, (tx, ty), ds0, do0) = tgt

    # If we can't win the chosen target, switch to the best potential one for net advantage.
    if ds0 > do0:
        best_adv = None
        for rx, ry in rpos_sorted:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = (do - ds)  # positive means we are closer
            key = (-adv, ds, rx, ry)
            if best_adv is None or key < best_adv[0]:
                best_adv = (key, (rx, ry), ds, do)
        (ds_adv_key, (tx, ty), ds0, do0) = best_adv[1], best_adv[2], best_adv[3]

    best_move = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        dself = cheb(nx, ny, tx, ty)
        dopp = cheb(ox, oy, tx, ty)

        # Primary: maximize reach advantage after our move for the target.
        # Secondary: minimize our distance to target.
        # Tertiary: keep away from opponent when ties (deterministic robustness).
        key1 = -(dopp - dself)
        key2 = dself
        key3 = -cheb(nx, ny, ox, oy)
        # Final deterministic tie-break on move ordering.
        move_key = (key1, key2, key3, dx, dy)
        if move_key < best_move:
            best_move = move_key

    return [int(best_move[3]), int(best_move[4])]