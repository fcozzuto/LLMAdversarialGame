def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

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
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                targets.append((x, y))
    if not targets:
        return [0, 0]

    # Innovation: pick a target that we can reach in fewer steps than opponent,
    # with deterministic center bias to break ties.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for tx, ty in targets:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        lead = od - sd  # positive means we are closer
        center_bias = -(abs(tx - cx) + abs(ty - cy)) * 0.001
        # Penalize if very far behind opponent (to avoid chasing lost races)
        behind_pen = -1000 if lead < 0 and sd > od else 0
        key = (behind_pen, lead, -sd, center_bias, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obs or not (0 <= nx < w and 0 <= ny < h):
        # Try axis-first deterministic fallback toward the same target.
        cand = []
        if dx != 0:
            cand.append((dx, 0))
        if dy != 0:
            cand.append((0, dy))
        if dx != 0 and dy != 0:
            cand.append((dx, dy))
        for ddx, ddy in cand:
            xx, yy = sx + ddx, sy + ddy
            if 0 <= xx < w and 0 <= yy < h and (xx, yy) not in obs:
                return [int(ddx), int(ddy)]
        return [0, 0]
    return [int(dx), int(dy)]