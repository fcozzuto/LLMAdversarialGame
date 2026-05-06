def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles_raw = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))

    if not rpos:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Nemesis-safe_collector pressure: if opponent is closer to a resource, try to "steal" by chasing
    # the one with maximum opponent lead over us (so we reduce their easiest path).
    best = None
    best_key = None
    for rp in rpos:
        sd = cheb((sx, sy), rp)
        od = cheb((ox, oy), rp)
        lead = od - sd  # positive means we are closer; negative means opponent closer
        # Primary: maximize our advantage (lead). If all negative, minimize their advantage magnitude.
        # Tie-break: prefer closer to us to avoid thrashing.
        key = (lead, -sd) if lead >= 0 else (lead, sd)
        if best_key is None or key > best_key:
            best_key = key
            best = rp

    tx, ty = best

    step_options = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministically pick the move that reduces Chebyshev distance to target and is not blocked.
    cur_d = cheb((sx, sy), (tx, ty))
    chosen = None
    chosen_d = None
    for dx, dy in step_options:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nd = cheb((nx, ny), (tx, ty))
        if nd <= cur_d:
            # Prefer largest improvement; tie-break by lexicographic move order deterministically.
            improv = cur_d - nd
            k = (improv, -abs(dx) - abs(dy), -nd, dx, dy)
            if chosen is None or k > chosen_d:
                chosen = (dx, dy)
                chosen_d = k

    if chosen is None:
        # Fallback: any in-bounds, non-blocked move closest to target
        for dx, dy in step_options:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            nd = cheb((nx, ny), (tx, ty))
            k = (-nd, dx, dy)
            if chosen is None or k > chosen_d:
                chosen = (dx, dy)
                chosen_d = k

    return [int(chosen[0]), int(chosen[1])]