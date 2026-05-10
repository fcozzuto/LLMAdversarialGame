def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a target resource: prioritize being closer than opponent; otherwise still contest nearest.
    best = None  # (priority, my, ot, rx, ry)
    for rx, ry in resources:
        my = man(sx, sy, rx, ry)
        ot = man(ox, oy, rx, ry)
        if my == 0 and (sx, sy) == (rx, ry):
            pr = -10**6
        else:
            # smaller priority is better
            # If we are closer, strongly prefer; if not, prefer closest to us but still penalize if opponent is much closer.
            pr = (0 if my <= ot else 1) * 10**6 + (my - ot)
        cand = (pr, my, ot, rx, ry)
        if best is None or cand < best:
            best = cand

    _, _, _, tx, ty = best

    # Anti-stuck: if our best target is "behind" due to obstacles, bias toward reducing distance anyway.
    # Also slightly avoid moving into cells adjacent to obstacles (deterministic).
    def obs_adj(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    cnt += 1
        return cnt

    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        # Prefer capturing if landing on target; otherwise minimize distance.
        capture_bonus = -2000 if (nx, ny) == (tx, ty) else 0
        # Mild tie-break to reduce obstacle-adjacent cells and avoid wandering.
        adj_pen = obs_adj(nx, ny) * 5
        # Deterministic tie-break using position ordering
        tie = (nx * 8 + ny)
        val = (d + adj_pen) + capture_bonus + tie * 0.000001
        if val < best_move[0]:
            best_move = (val, dx, dy)

    return [int(best_move[1]), int(best_move[2])]