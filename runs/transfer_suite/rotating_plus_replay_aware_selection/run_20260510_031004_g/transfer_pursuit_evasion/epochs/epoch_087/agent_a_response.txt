def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (w == 8 and h == 8) or True:
        # Prefer advancing order deterministically toward/away from opponent
        dx_dir = 0 if ox == sx else (1 if ox > sx else -1)
        dy_dir = 0 if oy == sy else (1 if oy > sy else -1)
        moves = sorted(moves, key=lambda m: -((m[0] == dx_dir) + (m[1] == dy_dir) + (m[0] * dx_dir > 0) + (m[1] * dy_dir > 0)))

    best_val = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**18 if self_is_pursuer else 10**18
        else:
            d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

            # Obstacle-aware local mobility (deterministic, cheap)
            mob = 0
            for adx, ady in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    mob += 1

            # Corner avoidance for evader; corner pursuit for pursuer
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_d2 = min((cx - nx) * (cx - nx) + (cy - ny) * (cy - ny) for cx, cy in corners)

            if self_is_pursuer:
                val = (-d2) + 0.15 * mob - 0.02 * corner_d2
            else:
                val = (d2) + 0.10 * mob - 0.03 * corner_d2

        if best_val is None or (self_is_pursuer and val > best_val) or ((not self_is_pursuer) and val > best_val):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]