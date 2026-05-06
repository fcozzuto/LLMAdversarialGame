def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = []
    for r in (observation.get("resources", []) or []):
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            resources.append((rx, ry))

    def clamp(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer resources where we are (strictly) closer than the opponent; otherwise deny by maximizing lead.
    best_t = None
    best_score = -10**9
    for rx, ry in resources:
        my_d = man((sx, sy), (rx, ry))
        opp_d = man((ox, oy), (rx, ry))
        # margin encourages grabbing contested resources; lead term denies.
        lead = opp_d - my_d
        contested_bonus = 15 if my_d <= opp_d - 1 else (7 if my_d == opp_d else 0)
        score = contested_bonus + lead * 3 - my_d
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t
    # Choose move that avoids obstacles and reduces distance to target; tie-break by moving away from opponent distance.
    cur_d = man((sx, sy), (tx, ty))
    best_m = (0, 0)
    best_ms = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = man((nx, ny), (tx, ty))
        d_from_opp = man((nx, ny), (ox, oy))
        # If staying is allowed, still handle: dx=dy=0 yields d_to_t==cur_d.
        ms = (cur_d - d_to_t) * 50 + (d_to_t == cur_d) * (-2) + d_from_opp * 0.1
        if ms > best_ms:
            best_ms = ms
            best_m = (dx, dy)

    # If all moves blocked (unlikely), fall back to staying.
    return [int(best_m[0]), int(best_m[1])]