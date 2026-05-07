def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except Exception:
            pass
    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = abs(ax - bx), abs(ay - by)
        return dx if dx > dy else dy

    # Pick a resource we're likely to reach before the opponent.
    # Primary: (opp_cheb - self_cheb). Secondary: closer for us. Tertiary: deterministic coords.
    best = None
    for t in resources:
        sd = cheb((sx, sy), t)
        od = cheb((ox, oy), t)
        key = (od - sd, -sd, -t[0], -t[1])
        if best is None or key > best[0]:
            best = (key, t)
    tx, ty = best[1]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Choose the move that improves race priority to the chosen target,
    # with obstacle safety; tie-break deterministically.
    cur_sd = cheb((sx, sy), (tx, ty))
    cur_od = cheb((ox, oy), (tx, ty))
    best_m, best_k = None, None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb((nx, ny), (tx, ty))
        # Opponent likely moves too; use current opp distance as a conservative anchor.
        ndiff = cur_od - nsd
        # Also add mild preference to reduce our distance even if racing is equal.
        k = (ndiff, -nsd, dx, dy)
        if best_k is None or k > best_k:
            best_k = k
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]