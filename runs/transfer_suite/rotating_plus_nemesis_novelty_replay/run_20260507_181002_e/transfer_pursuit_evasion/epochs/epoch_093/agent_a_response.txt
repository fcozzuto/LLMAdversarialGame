def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evad" in role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    if is_evader:
        tx, ty = clamp(ox + (ox - sx), 0, w - 1), clamp(oy + (oy - sy), 0, h - 1)  # flee further along approach vector
        score_fn = lambda nx, ny: (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # maximize score_fn (go away)
        best = -10**18
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            val = score_fn(nx, ny)
            if val > best:
                best = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        # pursuer: cut off by aiming past the opponent (one-step intercept heuristic)
        ix, iy = clamp(ox + (ox - sx), 0, w - 1), clamp(oy + (oy - sy), 0, h - 1)
        # minimize distance to intercept; tie-break toward opponent
        best = 10**18
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            di = (nx - ix) * (nx - ix) + (ny - iy) * (ny - iy)
            dp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            # small bias to keep toward center for robustness
            center_bias = (nx - (w - 1) / 2) * (nx - (w - 1) / 2) + (ny - (h - 1) / 2) * (ny - (h - 1) / 2)
            val = di * 4 + dp * 2 + int(center_bias)
            if val < best:
                best = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]