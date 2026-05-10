def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in self_role) or ("pursue" in self_role)
    if ("pursuer" in opp_role) and not (("pursuer" in self_role) or ("pursue" in self_role)):
        pursuer = False

    obs_set = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs_set.add((int(b[0]), int(b[1])))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    def clamp_move(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def score(nx, ny):
        d = abs(nx - ox) + abs(ny - oy)
        if pursuer:
            base = -d
        else:
            base = d
        risk = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs_set:
                    risk -= 3
        if (nx, ny) in obs_set:
            risk -= 1000
        return base + risk + (-(nx + ny) if pursuer else (nx + ny))

    for i, (dx, dy) in enumerate(deltas):
        nx, ny = clamp_move(sx + dx, sy + dy)
        v = score(nx, ny)
        if best is None or v > best_val:
            best_val = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]