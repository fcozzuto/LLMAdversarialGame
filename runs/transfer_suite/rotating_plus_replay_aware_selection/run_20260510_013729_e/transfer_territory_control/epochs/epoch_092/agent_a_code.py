def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    candidates = []
    for key in ("unclaimed_cells", "opponent_territory"):
        for p in (observation.get(key) or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if ok(x, y):
                    candidates.append((x, y))

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best_move, best_score = [0, 0], -10**9

    # Prefer moving toward nearest candidate; otherwise keep position or try a safe move.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if candidates:
            dmin = 10**9
            for x, y in candidates[:200]:
                d = abs(x - nx) + abs(y - ny)
                if d < dmin:
                    dmin = d
            score = -dmin
        if dx == 0 and dy == 0:
            score -= 1  # discourage stalling
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move