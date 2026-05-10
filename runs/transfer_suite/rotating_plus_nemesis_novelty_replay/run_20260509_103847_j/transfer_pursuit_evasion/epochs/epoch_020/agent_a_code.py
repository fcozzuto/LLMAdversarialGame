def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            obs.add((int(p["x"]), int(p["y"])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict) and "x" in r and "y" in r:
            targets.append((int(r["x"]), int(r["y"])))

    # If resources likely exist, go for nearest; otherwise head to center while keeping distance from opponent.
    have_targets = bool(targets) and (observation.get("remaining_resource_count", 1) not in (0, "0", None, "None"))
    tx, ty = (w // 2, h // 2)
    if have_targets:
        best = None
        bd = None
        for x, y in targets:
            d = dist2(sx, sy, x, y)
            if bd is None or d < bd:
                bd = d
                best = (x, y)
        if best:
            tx, ty = best

    dxs = (-1, 0, 1)
    best_move = [0, 0]
    best_score = None

    for dx in dxs:
        for dy in dxs:
            nx, ny = int(sx) + dx, int(sy) + dy
            if not inb(nx, ny):
                continue
            # Score: prefer shorter distance to target; if no targets, prefer farther from opponent.
            d_target = dist2(nx, ny, tx, ty)
            d_opp = dist2(nx, ny, ox, oy)
            score = -d_target
            if not have_targets:
                score = d_opp * 2 - d_target
            # Small deterministic tie-breaker: prioritize staying only if equal later.
            score += (0 if (dx == 0 and dy == 0) else 0)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move