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

    pursuer = ("purs" in self_role) or ("hunter" in self_role) or (self_role == "pursuer")
    if not pursuer and opponent_role:
        pursuer = not ("evad" in opponent_role)
    if not self_role and opponent_role:
        pursuer = not ("evad" in opponent_role)
    if not opponent_role and not self_role:
        pursuer = True  # safe default

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    def d2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = d2(nx, ny)
        # If pursuer: minimize distance; if evader: maximize distance.
        # Tie-break deterministically to reduce dithering.
        tie = (nx * 97 + ny * 53 + dx * 7 + dy * 11)
        val = dist if not pursuer else -dist
        if best is None or val > best_val or (val == best_val and tie < best[2]):
            best = (dx, dy, tie)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]