def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas = moves

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

    if not resources:
        # no resources: move to maximize distance from opponent while avoiding obstacles
        best = (None, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            val = cd(nx, ny, ox, oy)
            if val > best[1]:
                best = ((dx, dy), val)
        return list(best[0] if best[0] else (0, 0))

    # Choose target resource where we have the biggest reach advantage (opponent farther than us).
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cd(sx, sy, rx, ry)
        do = cd(ox, oy, rx, ry)
        # Prefer more advantage; tie-break by closer overall to us; deterministic by coords.
        key = (-(do - ds), ds + do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t

    def obstacle_adj_pen(x, y):
        p = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in obstacles:
                p += 1
        return p

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: reduce distance to target; Secondary: avoid giving opponent a better shot.
        ds_now = cd(sx, sy, rx, ry)
        ds_next = cd(nx, ny, rx, ry)
        do_now = cd(ox, oy, rx, ry)
        do_next = cd(ox, oy, rx, ry)  # opponent doesn't move now; keep consistent

        # Also try to keep distance from opponent (prevents being herded).
        opp_dist = cd(nx, ny, ox, oy)

        # Penalties: adjacency to obstacles.
        val = (ds_now - ds_next) * 1000 + (opp_dist) - obstacle_adj_pen(nx, ny) * 5

        # If we can reach target immediately, heavily prioritize.
        if ds_next == 0:
            val += 10**9

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]