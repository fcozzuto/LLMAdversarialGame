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
    if ("evad" in self_role):
        pursuer = False

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    # Deterministic tie-break: prefer diagonal then horizontal/vertical, then staying last.
    dir_rank = {d: i for i, d in enumerate(dirs)}

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d2 = dist2(nx, ny)

        # Pursuer wants smaller distance; Evader wants larger.
        base = d2 if pursuer else -d2

        # Wall/near-obstacle penalty to avoid getting boxed in (both roles benefit slightly).
        near = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obs:
                    near += 1

        # Small bias to move in the most "useful" direction relative to opponent.
        sx2 = 0
        if dx == 0 and dy == 0:
            sx2 = -0.01
        # If pursuer, prefer stepping toward opponent; if evader, prefer stepping away.
        toward = ((nx - ox) * (sx - ox) + (ny - oy) * (sy - oy))
        dir_bias = 0.0
        if pursuer:
            dir_bias = -0.001 * toward
        else:
            dir_bias = 0.001 * toward

        score = base - 0.02 * near + sx2 + dir_bias

        if best is None:
            best = (score, dir_rank[(dx, dy)], dx, dy)
        else:
            if score < best[0] if pursuer else score > best[0]:
                best = (score, dir_rank[(dx, dy)], dx, dy)
            elif score == best[0]:
                if dir_rank[(dx, dy)] < best[1]:
                    best = (score, dir_rank[(dx, dy)], dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]