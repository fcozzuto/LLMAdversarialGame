def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed_list = observation.get("unclaimed_cells") or []
    unclaimed = set(tuple(p) for p in unclaimed_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in oppT:
            base = 20
        elif (nx, ny) in unclaimed:
            base = 14
        elif (nx, ny) in selfT:
            base = 0
        else:
            base = 6

        # Prefer moving to contested zones (closer to opponent) and towards center a bit.
        dist_opp = man(nx, ny, ox, oy)
        dist_center = man(nx, ny, w // 2, h // 2)
        # Tie-breakers favor diagonal advancement and staying away from obstacles implicitly by scoring.
        diag_bonus = 2 if dx != 0 and dy != 0 else 0
        score = base * 100 - dist_opp * 8 - dist_center * 0.7 + diag_bonus

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    # If fully blocked, attempt a deterministic stay; engine will keep in place anyway.
    return [0, 0]