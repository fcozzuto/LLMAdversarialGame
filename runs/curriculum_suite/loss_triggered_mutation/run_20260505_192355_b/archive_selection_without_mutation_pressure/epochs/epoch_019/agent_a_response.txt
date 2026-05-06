def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Deterministic "sweep" preference: keep moving toward increasing y (overall),
    # and use x-parity alternation to spread across rows.
    sweep_x = w - 1 if (sy % 2 == 0) else 0
    prefer_dir = (1 if sweep_x > sx else -1 if sweep_x < sx else 0, 1 if oy >= sy else 0)

    best_move = [0, 0]
    best_score = -10**18

    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue

            # Local directional shaping
            dir_shape = 0
            if dx != 0:
                dir_shape += 0.8 if dx == prefer_dir[0] else -0.3
            if dy != 0:
                dir_shape += 0.8 if dy == prefer_dir[1] else -0.3

            # Choose best target resource under a "contest / deny" lead heuristic.
            cand = -10**18
            for rx, ry in resources:
                self_d = man(nx, ny, rx, ry)
                opp_d = man(ox, oy, rx, ry)

                # Lead drives contest; also heavily prefer reducing opponent's access when we're behind.
                lead = opp_d - self_d
                contest = 20.0 * lead - 1.2 * self_d

                # If opponent is very close to a resource, prioritize moves that shrink their distance too.
                opp_pressure = 0.0
                if opp_d <= 3:
                    opp_pressure = 6.0 * (man(ox, oy, rx, ry) - self_d) - 0.8 * opp_d

                # Mild reward for aligning with opponent row/nearby rows (denial zone).
                row_zone = 2.0 if abs(ry - oy) <= 1 else 0.0

                # Encourage capturing resources earlier along the global y sweep.
                y_push = 0.0
                if dy > 0:
                    y_push = 0.6 * (ry - ny)
                cand = max(cand, contest + opp_pressure + row_zone + y_push)

            score = cand + dir_shape
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move