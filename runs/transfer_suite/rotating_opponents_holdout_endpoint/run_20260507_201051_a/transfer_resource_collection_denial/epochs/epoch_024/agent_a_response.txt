def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def parse_pos(r):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return int(r[0]), int(r[1])
        if isinstance(r, dict):
            pos = r.get("position", r.get("pos", None))
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                return int(pos[0]), int(pos[1])
        return None

    targets = []
    for r in resources:
        p = parse_pos(r)
        if p:
            x, y = p
            if inb(x, y) and (x, y) not in obs:
                targets.append((x, y))
    if not targets:
        return [0, 0]

    ox, oy = observation["opponent_position"]
    best = None
    best_score = -10**9
    # Deterministic tie-breaking by (score desc, x desc, y desc)
    for tx, ty in sorted(targets, key=lambda z: (z[0], z[1]), reverse=True):
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        score = (od - sd) * 100 - sd  # prefer where we are closer than opp
        if score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                dist = abs(tx - nx) + abs(ty - ny)
                cand.append((dist, -dx, -dy, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    _, _, _, dx, dy = cand[0]
    return [int(dx), int(dy)]