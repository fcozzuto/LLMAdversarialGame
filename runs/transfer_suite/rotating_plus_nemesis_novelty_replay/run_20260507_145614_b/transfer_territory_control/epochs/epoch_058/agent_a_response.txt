def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2]
    unclaimed_set = set(unclaimed)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Build a small deterministic target set: closest unclaimed and a few closest opponent territory cells.
    targets = []
    if unclaimed:
        key = min(unclaimed, key=lambda t: (dist(sx, sy, t[0], t[1]), t[0], t[1]))
        targets.append(key)
    if oppT:
        # Pick up to 6 opponent cells with smallest distance to us.
        best_opp = sorted(oppT, key=lambda t: (dist(sx, sy, t[0], t[1]), t[0], t[1]))[:6]
        targets.extend(best_opp)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Immediate claim/flip preference
        if (nx, ny) in oppT:
            base = 3.0
        elif (nx, ny) in unclaimed_set:
            base = 1.3
        elif (nx, ny) in selfT:
            base = 0.2
        else:
            base = 0.6
        # Pressure term: move closer to best target, and also away from opponent to avoid losing tempo
        if targets:
            dmin = min(dist(nx, ny, tx, ty) for tx, ty in targets)
            dopp = dist(nx, ny, ox, oy)
            pressure = -0.06 * dmin + 0.02 * dopp
        else:
            pressure = 0.01 * dist(nx, ny, ox, oy)  # fallback: mild drift
        # Slight tie-breaker to avoid obstacles sticking: prefer not-staying if equally good
        stay_pen = 0.05 if (dx == 0 and dy == 0) else 0.0
        score = base + pressure - stay_pen

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]