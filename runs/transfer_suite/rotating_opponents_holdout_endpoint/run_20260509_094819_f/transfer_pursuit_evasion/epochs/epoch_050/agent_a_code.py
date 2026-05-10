def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role") or "")
    pursuer = ("purs" in role.lower()) or (role.lower() == "pursuer")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked
    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy
    def step_options(px, py):
        opts = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if inb(nx, ny):
                opts.append((dx, dy, nx, ny))
        if not opts:
            opts = [(0, 0, px, py)]
        return opts

    my_opts = step_options(sx, sy)
    opp_opts = step_options(ox, oy)

    best = (0, 0)
    best_val = None

    # tie-breakers for determinism
    opp_turn = 1 if pursuer else -1

    for dx, dy, nx, ny in my_opts:
        worst = None
        # If we are pursuer: opponent tries to maximize distance from our new position.
        # If we are evader: opponent (pursuer) tries to minimize distance from our new position.
        for odx, ody, tx, ty in opp_opts:
            d = dist2(nx, ny, tx, ty)
            val = d
            if worst is None:
                worst = val
            else:
                if pursuer:
                    if val > worst: worst = val
                else:
                    if val < worst: worst = val

        # slight obstacle/edge pressure to avoid getting trapped near obstacles
        near_obs = 0
        for (bx, by) in blocked:
            if abs(nx - bx) <= 1 and abs(ny - by) <= 1:
                near_obs += 1
        edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
        score = worst - 0.25 * near_obs + (0.05 if edge else 0.0) * opp_turn

        if best_val is None or (pursuer and score < best_val) or ((not pursuer) and score > best_val):
            best_val = score
            best = (dx, dy)
        elif best_val is not None:
            if score == best_val:
                if (dx, dy) < best:
                    best = (dx, dy)

    return [int(best[0]), int(best[1])]