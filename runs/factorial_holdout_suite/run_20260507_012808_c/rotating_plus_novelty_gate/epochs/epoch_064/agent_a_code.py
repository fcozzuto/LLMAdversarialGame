def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Evaluate by who can reach the same resource sooner; also bias toward closer resources.
    best = (float("-inf"), None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx = 0 if nx < 0 else (w - 1 if nx >= w else nx)
        ny = 0 if ny < 0 else (h - 1 if ny >= h else ny)
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        if resources:
            best_margin = float("-inf")
            best_dist = 10**9
            # Deterministic: iterate sorted resources
            for tx, ty in sorted(resources):
                md = man(nx, ny, tx, ty)
                od = man(ox, oy, tx, ty)
                margin = od - md  # positive means we are closer than opponent
                if margin > best_margin or (margin == best_margin and md < best_dist) or (margin == best_margin and md == best_dist and (tx, ty) < (tx, ty)):
                    best_margin = margin
                    best_dist = md
            # Turn urgency: when few turns remain, prioritize immediate pickup more
            tr = int(observation.get("turns_remaining") or 0)
            urgency = 1.0 if tr <= 10 else (0.7 if tr <= 24 else 0.45)
            val = best_margin + urgency * (-best_dist * 0.01)
        else:
            # No visible resources: move to reduce distance to opponent-checked corner clusters deterministically
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            tx, ty = min(corners, key=lambda p: (man(ox, oy, p[0], p[1]), p[0], p[1]))
            val = -man(nx, ny, tx, ty)
        if val > best[0]:
            best = (val, [dx, dy])
    return best[1]