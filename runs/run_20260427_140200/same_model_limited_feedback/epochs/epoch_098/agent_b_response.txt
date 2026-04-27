def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((x, y) for x, y in obstacles)
    if not resources:
        # fallback: move away from opponent a bit, prefer diagonals
        best = (10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set:
                    d = max(abs(nx - ox), abs(ny - oy))
                    score = (-d, abs(dx) + abs(dy), dx + 2 * dy)
                    if score < (best[0], best[1], best[2]):
                        best = (score[0], score[1], score[2])
        # decode
        dx_best = 0; dy_best = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set:
                    d = max(abs(nx - ox), abs(ny - oy))
                    sc = (-d, abs(dx) + abs(dy), dx + 2 * dy)
                    if sc == (best[0], best[1], best[2]):
                        dx_best, dy_best = dx, dy
        return [dx_best, dy_best]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # pick resource where we have greatest arrival advantage over opponent
    best_res = None
    best_key = None
    for r in resources:
        rd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        key = (rd - od, rd, r[0], r[1])  # smaller is better
        if best_key is None or key < best_key:
            best_key = key
            best_res = r

    tx, ty = best_res
    # choose move: go toward target; if very close, also keep distance from opponent
    close = dist((sx, sy), (ox, oy)) <= 2
    best = None
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacle_set:
                continue
            nd = dist((nx, ny), (tx, ty))
            opp_d = dist((nx, ny), (ox, oy))
            step_pen = abs(dx) + abs(dy)
            # Prefer reducing distance to target; avoid opponent when close
            if close:
                score = (nd, step_pen, -opp_d, dx + 2 * dy)
            else:
                score = (nd, step_pen, dx + 2 * dy)
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]