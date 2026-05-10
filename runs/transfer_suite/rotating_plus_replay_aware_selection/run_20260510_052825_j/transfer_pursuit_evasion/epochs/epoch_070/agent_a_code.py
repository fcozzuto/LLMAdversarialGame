def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in role) or ("pursuer" in role)

    def neighbors_free(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    # Deterministic order tie-break: prefer moves earlier in list
    parity_goal = (ox + oy) & 1
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        md = abs(nx - ox) + abs(ny - oy)
        deg = neighbors_free(nx, ny)
        on_edge = (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1)
        parity = (nx + ny) & 1

        if is_pursuer:
            # Chase exactly, but avoid getting trapped by edges/low-mobility.
            score = (-10 * md) + (2.0 * deg) + (-0.8 * on_edge) + (0.6 if parity == parity_goal else 0.0)
            # If multiple moves reduce distance equally, prefer the one that moves "more aligned" toward target.
            align = (1 if (nx - sx) == (ox - sx) and nx != sx else 0) + (1 if (ny - sy) == (oy - sy) and ny != sy else 0)
            score += 0.15 * align
        else:
            # Evade: maximize distance; prefer mobility and avoid letting pursuer corner-lock you.
            # Also avoid stepping onto edge too early.
            score = (10 * md) + (1.8 * deg) + (-1.2 * on_edge) + (-0.4 if parity == parity_goal else 0.0)

        if best is None or score > best:
            best = score
            best_move = [dx, dy]
    return best_move