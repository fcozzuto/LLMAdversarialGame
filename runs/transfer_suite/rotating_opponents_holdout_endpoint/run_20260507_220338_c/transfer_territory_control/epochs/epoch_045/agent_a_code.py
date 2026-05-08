def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            obs_set.add((x, y))

    self_t = set()
    for p in (observation.get("self_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_t.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed_set = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y) and (x, y) not in obs_set:
                unclaimed_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    adj_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp = (ox, oy)
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        cell = (nx, ny)
        if cell in self_t:
            base = 1
        elif cell in unclaimed_set:
            base = 8
        elif cell in opp_t:
            base = 30
        else:
            base = 3  # likely empty but in bounds
        # Prefer stepping toward safe front (farther from opponent) while taking flips.
        d_opp = man(cell, opp)
        safety = d_opp * 0.6
        # Prefer moving to cells that border many unclaimed (expansion) and avoid immediate traps.
        border_un = 0
        border_opp = 0
        for ax, ay in adj_dirs:
            ax2, ay2 = nx + ax, ny + ay
            if not in_bounds(ax2, ay2) or (ax2, ay2) in obs_set:
                continue
            if (ax2, ay2) in unclaimed_set:
                border_un += 1
            if (ax2, ay2) in opp_t:
                border_opp += 1
        expansion = border_un * 1.2
        danger = border_opp * 0.9
        # Deterministic tie-break: closer to opposite corner than to opponent.
        corner = (w - 1, h - 1) if (sx + sy) < (ox + oy) else (0, 0)
        corner_bias = -man(cell, corner) * 0.05 - man(cell, opp) * 0.05
        score = base + safety + expansion + corner_bias - danger
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best