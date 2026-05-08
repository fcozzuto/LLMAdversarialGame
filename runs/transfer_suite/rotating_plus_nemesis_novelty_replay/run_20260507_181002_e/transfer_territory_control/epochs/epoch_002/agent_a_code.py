def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]

    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    x, y = (sp[0], sp[1]) if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = (op[0], op[1]) if isinstance(op, (list, tuple)) and len(op) >= 2 else (0, 0)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    targets = set()
    for p in (observation.get("unclaimed_cells", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.add((p[0], p[1]))
    if not targets:
        for p in (observation.get("resources", []) or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.add((p[0], p[1]))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = None

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    opp_territory = set()
    for p in (observation.get("opponent_territory", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_territory.add((p[0], p[1]))

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer stepping closer to nearest target; lightly punish closeness to opponent.
        if targets:
            dist = min(man(nx, ny, tx, ty) for tx, ty in targets)
        else:
            dist = man(nx, ny, ox, oy)
        opp_pen = 0
        if (nx, ny) in opp_territory:
            opp_pen = 50
        score = dist + opp_pen + (man(nx, ny, ox, oy) // 4)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        # Deterministic fallback: try four cardinal moves toward opponent, avoiding obstacles/bounds.
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]