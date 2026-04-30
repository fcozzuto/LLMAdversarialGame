def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return abs(dx) + abs(dy)

    # Pick a target resource by maximum "race advantage" (opponent farther than us).
    if resources:
        best = None
        for rx, ry in resources:
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            # Prefer immediate adjacency, and higher advantage; deterministic tie-break by position.
            adv = (od - sd)
            key = (adv, -sd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No visible resources: head toward center as a fallback.
        tx, ty = (w // 2), (h // 2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (None, -10**9)
    res_set = set(tuple(p) for p in resources)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        blocked = (nx, ny) in obstacles
        nd = dist((nx, ny), (tx, ty))
        # Avoid obstacles strongly; reward getting closer and collecting if adjacent.
        val = 0
        if blocked:
            val -= 10**6
        else:
            val += (w + h) - nd
            if (nx, ny) in res_set:
                val += 10**5
            # If we are not the race leader, slightly prioritize moving to improve our advantage.
            if resources:
                self_adv_after = (dist((ox, oy), (tx, ty)) - nd)
                val += self_adv_after * 10
            # Mild anti-oscillation: prefer moves that reduce distance to opponent less aggressively (still deterministic).
            # (No history available; keep it simple.)
        if val > best_move[1] or (val == best_move[1] and (dx, dy) < best_move[0]):
            best_move = ((dx, dy), val)

    return [best_move[0][0], best_move[0][1]]