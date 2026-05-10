def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Find opponent's closest resource (deterministic tie-break by position).
    opp_closest = None
    best_od = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if best_od is None or d < best_od or (d == best_od and (rx, ry) < opp_closest):
            best_od = d
            opp_closest = (rx, ry)
    tx, ty = opp_closest

    # Choose target with a different emphasis than pure nearest: race advantage, but
    # periodically invert to break loops.
    even = (int(observation.get("turn_index", 0)) % 2 == 0)
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Key components:
        # - Prefer resources we can reach no later than opponent.
        # - Otherwise, prefer maximizing opponent distance advantage.
        # - Small deterministic tie-break by coordinates.
        can_win = 1 if myd <= od else 0
        race = (od - myd)
        # Alternate objective to avoid repeating the same policy:
        # even: aggressive win-first; odd: denial-first (still deterministic).
        key = (can_win, race, -myd if even else od, rx, ry) if even else (can_win, race, -od, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Move one step toward target; if blocked, try alternate neighbor deterministically.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    cand = []
    # Prefer diagonal/greedy; then fall back in a fixed order.
    cand.append((dx, dy))
    cand.append((dx, 0))
    cand.append((0, dy))
    cand.append((dx, -dy))
    cand.append((-dx, dy))
    cand.append((0, 0))
    cand = [(cx, cy) for (cx, cy) in cand if cx in (-1, 0, 1) and cy in (-1, 0, 1)]

    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            return [mx, my]

    return [0, 0]