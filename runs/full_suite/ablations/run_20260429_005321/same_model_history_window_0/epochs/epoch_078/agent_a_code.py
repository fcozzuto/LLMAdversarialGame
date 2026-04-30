def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((x, y) for x, y in obstacles)

    def clamp(v, a, b):
        return a if v < a else b if v > b else v

    def king_dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose target resource: maximize (opp_dist - my_dist), then my_dist
    if resources:
        best = None
        for r in resources:
            if (r[0], r[1]) in obs_set:
                continue
            md = king_dist((sx, sy), r)
            od = king_dist((ox, oy), r)
            adv = od - md
            key = (adv, -md, -r[1], -r[0])  # deterministic tie-break
            if best is None or key > best[0]:
                best = (key, r)
        target = best[1] if best else None
    else:
        target = None

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        if target is not None:
            cur_d = king_dist((nx, ny), target)
            my_d = king_dist((sx, sy), target)
            # Prefer approaching target; also prefer keeping distance from opponent
            val = (-cur_d * 3) + ((my_d - cur_d) * 5) + (king_dist((nx, ny), (ox, oy)) * 1)
            # Small bias to not drift if already close
            if cur_d == my_d:
                val -= 0.25 * (abs(dx) + abs(dy))
        else:
            # If no resources, maximize distance to opponent
            val = king_dist((nx, ny), (ox, oy)) * 3 - (abs(dx) + abs(dy)) * 0.1

        # Deterministic tie-break: prefer moves with smaller dx, then smaller dy
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]