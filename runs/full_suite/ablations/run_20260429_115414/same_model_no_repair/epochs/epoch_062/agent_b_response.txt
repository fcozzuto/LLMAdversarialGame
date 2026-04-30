def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Pick a resource with best immediate capture advantage; tie-break by closer to self, then coordinates.
    best = None
    best_score = None
    best_sd = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd
        if best_score is None or adv > best_score or (adv == best_score and (best_sd is None or sd < best_sd)) or (adv == best_score and sd == best_sd and (rx, ry) < best):
            best_score, best_sd, best = adv, sd, (rx, ry)

    tx, ty = best
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = None
    prev_d = dist((sx, sy), (tx, ty))
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        nd = dist((nx, ny), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        # Prefer to reduce distance to target, and increase (opponent - self) advantage.
        # Small penalty for not improving.
        d_improve = prev_d - nd
        self_to_opp = dist((nx, ny), (ox, oy))
        val = (od - nd) * 100 - nd * 3 + d_improve * 5 - self_to_opp * 0.2
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]