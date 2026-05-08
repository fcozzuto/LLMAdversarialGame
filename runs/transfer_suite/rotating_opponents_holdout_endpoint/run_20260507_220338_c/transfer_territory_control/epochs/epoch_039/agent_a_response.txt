def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass
    self_t = set()
    for p in observation.get("self_territory") or []:
        try:
            self_t.add((int(p[0]), int(p[1])))
        except:
            pass
    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        try:
            opp_t.add((int(p[0]), int(p[1])))
        except:
            pass
    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.append((int(p[0]), int(p[1])))
        except:
            pass

    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)
    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer immediate capture if stepping into opponent territory is possible.
    best = None
    best_dxdy = (0, 0)
    best_val = -10**9

    # Use a small candidate set for determinism and brevity.
    candidates = unclaimed if unclaimed else list(opp_t)
    if not candidates:
        candidates = [(w - 1, h - 1), (0, h - 1), (w - 1, 0), (w // 2, h // 2)]
    # Deterministic pruning: keep nearest unclaimed to opponent (ties by coordinates).
    candidates = sorted(candidates, key=lambda t: (man(t[0], t[1], ox, oy), t[0], t[1]))[:12]

    # Cell preference model.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in opp_t:
            val += 220  # direct counterclaim
        if (nx, ny) not in self_t and (nx, ny) in set(unclaimed):
            val += 140  # secure unclaimed territory
        if (nx, ny) in self_t:
            val -= 15  # avoid wasting move inside already-owned area
        # Advance toward opponent while also preferring unclaimed near opponent.
        d_opp = man(nx, ny, ox, oy)
        val += (120 - d_opp)  # smaller distance is better
        # Avoid stepping away from the best frontier candidate.
        best_front = min(candidates, key=lambda t: (man(nx, ny, t[0], t[1]), t[0], t[1]))
        val += 25 - man(nx, ny, best_front[0], best_front[1])
        # Mild penalty for hugging the exact opponent position (prevents oscillation).
        val -= 0.5 * man(nx, ny, ox, oy) / 2.0
        # Deterministic tie-break: lexicographic on (dx,dy) after value.
        key = (val, -dx, -dy)
        if best is None or key > best:
            best = key
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]