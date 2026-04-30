def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose target deterministically using relative proximity to resources
    best = None
    best_val = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        # Prefer being closer than opponent; add small preference for earlier/leftmost deterministically
        val = (od - sd) * 1000 - sd
        if best is None or val > best_val or (val == best_val and (rx < best[0] or (rx == best[0] and ry < best[1]))):
            best_val = val
            best = (rx, ry)

    # Fallback if no reachable resources
    if best is None:
        tx, ty = (w // 2), (h // 2)
    else:
        tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Deterministically pick move that gets closer to target, avoids obstacles, and doesn't run toward opponent
    best_m = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        # Encourage reducing target distance and keeping away from opponent
        score = -myd * 10 + (dist((nx, ny), (ox, oy)) * 1.5)
        # Secondary: if target is around and opponent is competing, slightly prefer moves that maximize (opp_dist - self_dist)
        score += (opd - dist((nx, ny), (tx, ty))) * 0.5
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying
        if score > best_score or (score == best_score and (dx, dy) < best_m):
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]