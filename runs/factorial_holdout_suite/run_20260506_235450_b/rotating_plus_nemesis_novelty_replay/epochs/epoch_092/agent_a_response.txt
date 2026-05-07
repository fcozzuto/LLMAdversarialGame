def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    def manh(x, y):
        return abs(x - sx) + abs(y - sy)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in moves8:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                sc = -((abs(nx - cx) + abs(ny - cy)) * 1.0)
                if sc > best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    best_res = None
    best_score = -10**18
    for tx, ty in resources:
        my_d = abs(tx - sx) + abs(ty - sy)
        if opp_exists:
            opp_d = abs(tx - ox) + abs(ty - oy)
            # Prefer states where we are more competitive; add slight bias to closer self for collecting first.
            score = (opp_d - my_d * 1.15) - (0.02 * my_d)
        else:
            score = -my_d
        # Deterministic tie-break: higher score, then smaller my distance, then lexicographic
        if (score > best_score) or (score == best_score and (best_res is None or (my_d, tx, ty) < (abs(best_res[0]-sx)+abs(best_res[1]-sy), best_res[0], best_res[1]))):
            best_score = score
            best_res = (tx, ty)

    tx, ty = best_res
    dx_raw = 0 if tx == sx else (1 if tx > sx else -1)
    dy_raw = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx, dy in [(dx_raw, dy_raw), (dx_raw, 0), (0, dy_raw), (dx_raw, -dy_raw), (-dx_raw, dy_raw), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles and (dx, dy) in moves8:
            dnext = abs(tx - nx) + abs(ty - ny)
            candidates.append((dnext, abs(nx - ox) + abs(ny - oy) if opp_exists else 10**9, dx, dy))
    if not candidates:
        for dx, dy in moves8:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((abs(tx - nx) + abs(ty - ny), 0, dx, dy))
                break
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]