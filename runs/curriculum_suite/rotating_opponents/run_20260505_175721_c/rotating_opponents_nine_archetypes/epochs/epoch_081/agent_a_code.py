def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cd(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev distance for 8-neighborhood

    # Choose a resource we can reach sooner (or equivalently make ourselves closer than opponent)
    best = None
    best_val = None
    for tx, ty in resources:
        sd = cd((sx, sy), (tx, ty))
        od = cd((ox, oy), (tx, ty))
        # Favor winning races; add slight tie-break to reduce distance and vary by turn deterministically.
        val = (sd - od * 1.0) * 100 + sd
        if observation.get("turn_index", 0) is not None:
            val += ((tx * 3 + ty * 7 + int(observation.get("turn_index", 0))) % 5) * 0.01
        if best is None or val < best_val:
            best = (tx, ty)
            best_val = val

    # Candidate moves (keep within bounds and avoid obstacles)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if best is None:
        # No resources: move to center-ish deterministically
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # If we aren't clearly racing (sd >= od), try to "shadow" opponent: move to reduce od faster than sd
    sd_best = cd((sx, sy), (tx, ty))
    od_best = cd((ox, oy), (tx, ty))
    shadow = (best is None) or (sd_best >= od_best)

    cur = (sx, sy)
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cd((nx, ny), (tx, ty))
        if not shadow:
            # Greedy race to target; slight repulsion from opponent to avoid accidental gifting.
            score = nd * 10 + cd((nx, ny), (ox, oy)) * 0.2
        else:
            # Shadow: minimize opponent distance to that same target more than ours
            no = cd((ox, oy), (tx, ty))
            # Our next makes opponent path worse if it increases their distance, but they move too;
            # proxy: minimize our distance while ensuring opponent doesn't become significantly closer than us.
            score = (nd - cd((ox, oy), (tx, ty))) * 10 + nd
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]