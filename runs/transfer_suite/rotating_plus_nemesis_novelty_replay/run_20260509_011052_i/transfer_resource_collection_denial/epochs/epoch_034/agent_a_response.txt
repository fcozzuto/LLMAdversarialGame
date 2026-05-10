def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    rem = int(observation.get("remaining_resource_count", len(res)) or len(res))
    near_end = 1 if rem <= 6 else 0

    # Pick a resource: when near end, prioritize "steal chances" (make opp slower than me).
    # Otherwise, prioritize securing closest advantage.
    scored = []
    for x, y in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Higher steal_edge is better; include my speed as tie-breaker.
        steal_edge = (do - ds) if near_end else (do - ds) * 2 - ds * 0.15
        # Also discourage very long routes.
        penalty = ds * (0.05 if near_end else 0.1)
        scored.append((-steal_edge + penalty, ds, x, y))
    scored.sort()
    _, _, tx, ty = scored[0]

    def sign(a):
        if a > 0:
            return 1
        if a < 0:
            return -1
        return 0

    want_dx = sign(tx - sx)
    want_dy = sign(ty - sy)

    candidates = []
    # Prefer diagonal towards target; if blocked, try remaining axes towards target.
    if want_dx != 0 and want_dy != 0:
        candidates.append((want_dx, want_dy))
        candidates.append((want_dx, 0))
        candidates.append((0, want_dy))
    else:
        candidates.append((want_dx, want_dy))
        candidates.append((want_dx, 0))
        candidates.append((0, want_dy))
    # Deterministic fallbacks: nearest alternatives
    candidates += [(-want_dx, want_dy), (want_dx, -want_dy), (0, 0)]

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            return [int(dx), int(dy)]

    return [0, 0]