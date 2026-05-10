def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    if not (0 <= sx < w and 0 <= sy < h):
        sx, sy = 0, 0
    if not (0 <= ox < w and 0 <= oy < h):
        ox, oy = w - 1, h - 1

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    opponent_role = str(observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role)
    if "evader" in self_role:
        pursuer = False
    if (("pursuer" in opponent_role) or ("pursuit" in opponent_role) or ("hunter" in opponent_role)):
        if not ("evader" in self_role):
            pursuer = True

    dx_dir = 1 if ox > sx else (-1 if ox < sx else 0)
    dy_dir = 1 if oy > sy else (-1 if oy < sy else 0)
    if not pursuer:
        dx_dir, dy_dir = -dx_dir, -dy_dir

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        nxv, nyv = nx, ny
        dist2 = (nxv - ox) * (nxv - ox) + (nyv - oy) * (nyv - oy)
        align = -(dx * dx_dir + dy * dy_dir)
        # pursuer: minimize dist2; evader: maximize dist2 (by minimizing negative dist2)
        key = dist2 if pursuer else -dist2
        scored.append((key, align, dx, dy))
    if scored:
        scored.sort()
        return [int(scored[0][2]), int(scored[0][3])]

    # fallback: try deterministic in-bounds non-obstacle else stay
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [int(dx), int(dy)]
    return [0, 0]