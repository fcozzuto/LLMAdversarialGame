def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    opp_set = set()
    for c in observation.get("opponent_territory") or []:
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                opp_set.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dman(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def adj_to_op(tx, ty):
        for dx, dy in dirs[:-1]:
            if (tx + dx, ty + dy) in opp_set:
                return True
        return False

    # Prefer expanding into safe unclaimed far from the opponent; fall back to any unclaimed.
    best = None
    best_score = None
    any_unclaimed = False
    for c in unclaimed:
        if not c or len(c) < 2:
            continue
        tx, ty = int(c[0]), int(c[1])
        if not inb(tx, ty) and (tx, ty) not in opp_set:
            continue
        any_unclaimed = True
        dist_self = dman(sx, sy, tx, ty)
        dist_opp = dman(ox, oy, tx, ty)
        unsafe = 1 if adj_to_op(tx, ty) else 0
        # Score: smaller is better
        score = dist_self + 2.0 * unsafe - 0.55 * dist_opp
        if best_score is None or score < best_score or (score == best_score and (tx, ty) < best):
            best_score = score
            best = (tx, ty)

    if not any_unclaimed:
        # If nothing unclaimed, try to move away from opponent while respecting obstacles.
        best = (max(0, min(w - 1, sx + (sx > ox) - (sx < ox))), max(0, min(h - 1, sy + (sy > oy) - (sy < oy))))

    tx, ty = best

    # Choose a move that greedily approaches target, but discourages closeness to opponent.
    chosen = (0, 0)
    chosen_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) and (nx, ny) not in opp_set:
            continue
        approach = dman(nx, ny, tx, ty)
        away = dman(nx, ny, ox, oy)
        # tie-break deterministically by dx,dy ordering as listed
        key = (approach, -away, dx, dy)
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]