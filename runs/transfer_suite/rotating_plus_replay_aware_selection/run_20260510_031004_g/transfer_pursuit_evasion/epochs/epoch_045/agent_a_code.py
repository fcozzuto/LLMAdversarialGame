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
    if not pursuer and opponent_role:
        pursuer = not ("evad" in opponent_role)
    if not self_role and not opponent_role:
        pursuer = True

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def score(nx, ny):
        dx, dy = nx - ox, ny - oy
        d2 = dx * dx + dy * dy
        # Small tie-break to reduce oscillation: prefer moving in the direction that changes x/y earlier.
        t = (abs(nx - sx) + abs(ny - sy))
        return (d2, -t) if pursuer else (-d2, -t)

    best = None
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = score(nx, ny)
        if best is None:
            best, best_s = [dx, dy], s
        else:
            if pursuer:
                if s[0] < best_s[0] or (s[0] == best_s[0] and s[1] > best_s[1]):
                    best, best_s = [dx, dy], s
            else:
                if s[0] < best_s[0] or (s[0] == best_s[0] and s[1] > best_s[1]):
                    best, best_s = [dx, dy], s

    if best is not None:
        return [int(best[0]), int(best[1])]

    # Fallback: stay still if all moves blocked or invalid.
    return [0, 0]