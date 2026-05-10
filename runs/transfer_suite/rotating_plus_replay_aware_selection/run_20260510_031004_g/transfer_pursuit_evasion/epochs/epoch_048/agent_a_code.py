def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("hunter" in self_role) or (self_role == "pursuer") or (self_role == "pursuer_agent")
    if not self_role and opponent_role:
        pursuer = not ("evad" in opponent_role)
    if not self_role and not opponent_role:
        pursuer = True

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = [0, 0]
    best_val = None

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        mdx, mdy = nx - ox, ny - oy
        d2 = mdx * mdx + mdy * mdy
        # Pursuer: minimize distance; Evader: maximize distance.
        center_pen = ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.001
        val = (d2 if not pursuer else -d2) - center_pen
        # Deterministic tie-break favoring staying aligned with goal direction
        align = abs((nx - ox) * (sx - ox) + (ny - oy) * (sy - oy)) * 0.00001
        val = val + (align if not pursuer else align)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move