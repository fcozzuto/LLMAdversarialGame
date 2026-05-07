def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources or w <= 0 or h <= 0:
        return [0, 0]

    def cd(px, py, tx, ty):
        dx = abs(tx - px)
        dy = abs(ty - py)
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cd(sx, sy, rx, ry)
        do = cd(ox, oy, rx, ry)
        # Prefer resources we reach sooner; break ties by nearer to us, then deterministic by coords
        key = (do - ds, -ds, -(rx * 10 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Deterministic move selection among valid deltas: minimize distance to target, prefer those improving lead
    best_move = (0, 0)
    best_md = None
    best_lead = None
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue
        ds2 = cd(nsx, nsy, tx, ty)
        do = cd(ox, oy, tx, ty)
        lead = do - ds2
        if best_md is None or (ds2 < best_md) or (ds2 == best_md and lead > best_lead) or (ds2 == best_md and lead == best_lead and (mdx, mdy) < best_move):
            best_md = ds2
            best_lead = lead
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]