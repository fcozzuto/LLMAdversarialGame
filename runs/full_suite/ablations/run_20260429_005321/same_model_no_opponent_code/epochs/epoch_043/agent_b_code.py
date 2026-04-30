def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(px, py):
        return 0 <= px < w and 0 <= py < h and (px, py) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def rel_lead_to_target(tx, ty):
        ds = d2(x, y, tx, ty)
        do = d2(ox, oy, tx, ty)
        return ds - do  # smaller means we are closer (in squared distance)

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            val = rel_lead_to_target(rx, ry)
            tiebreak = (rx, ry)
            if best is None or val < best[0] or (val == best[0] and tiebreak < best[1]):
                best = (val, tiebreak)
        target = (best[1][0], best[1][1])
    else:
        # no resources visible: drift to opponent side deterministically
        target = (w - 1 if x < w - 1 else 0, h - 1 if y < h - 1 else 0)

    tx, ty = target
    best_move = (0, 0)
    best_score = None

    for dxm, dym in moves:
        nx, ny = x + dxm, y + dym
        if not ok(nx, ny):
            continue
        ds_next = d2(nx, ny, tx, ty)
        do_now = d2(ox, oy, tx, ty)
        rel_next = ds_next - do_now
        # Prefer reaching target while increasing our relative lead; slight penalty for moving closer to opponent.
        close_to_opp = d2(nx, ny, ox, oy)
        score = rel_next * 3 + ds_next + (1 if close_to_opp < d2(x, y, ox, oy) else 0)
        if best_score is None or score < best_score or (score == best_score and (dxm, dym) < best_move):
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]