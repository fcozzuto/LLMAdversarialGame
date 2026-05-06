def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, move to maximize distance from opponent while avoiding obstacles.
    if not resources:
        best = (None, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = cheb(nx, ny, ox, oy)
            if v > best[1] or (v == best[1] and (dx, dy) < best[0]):
                best = ((dx, dy), v)
        return [best[0][0], best[0][1]]

    # Choose a resource to contest: prefer cells where we're not slower than opponent; otherwise pick best compromise.
    best_res = resources[0]
    best_key = None  # (quality, -ts, tie)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ts = cheb(sx, sy, rx, ry)
        to = cheb(ox, oy, rx, ry)
        quality = to - ts
        # Prefer winning/contesting (quality >= 0), then larger quality, then closer.
        key = ((quality >= 0, quality), -ts, (rx, ry))
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res

    # Step towards target with obstacle avoidance; also lightly keep away from opponent if tie.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nt = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target. Secondary: increase distance from opponent. Tertiary: deterministic tie-break.
        score = (nt, -no, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]