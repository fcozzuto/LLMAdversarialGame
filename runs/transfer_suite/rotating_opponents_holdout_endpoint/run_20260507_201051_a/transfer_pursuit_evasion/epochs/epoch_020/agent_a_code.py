def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w, h = int(w), int(h)

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2 and p[0] is not None and p[1] is not None:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2 and r[0] is not None and r[1] is not None:
            resources.append((int(r[0]), int(r[1])))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("chase" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    if resources:
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            md = None
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if md is None or d < md:
                    md = d
            if md is None:
                continue
            val = -md
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        best_val = -10**18 if is_pursuer else 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = max(abs(nx - ox), abs(ny - oy))  # Chebyshev distance
            if is_pursuer:
                val = -d  # minimize distance
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]
            else:
                val = d  # maximize distance
                if val < best_val:
                    best_val = val
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]