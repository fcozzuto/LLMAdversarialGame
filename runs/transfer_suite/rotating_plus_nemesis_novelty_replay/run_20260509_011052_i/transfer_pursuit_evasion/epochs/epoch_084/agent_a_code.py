def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic ordering: prefer diagonals then straight then stay (via distance to center move)
    dirs.sort(key=lambda d: (d[0] == 0 and d[1] == 0, -(d[0] != 0 and d[1] != 0), -(abs(d[0]) + abs(d[1]))))

    # Two-step greedy lookahead (lightweight)
    best_move = (0, 0)
    best_score = None

    def step(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            return x, y
        return nx, ny

    for dx, dy in dirs:
        x1, y1 = step(sx, sy, dx, dy)
        d1 = cheb(x1, y1, ox, oy)

        # If pursuer: minimize distance to opponent.
        # If evader: maximize distance; additionally bias toward farthest corner for robustness.
        if not is_pursuer:
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far = max(cheb(x1, y1, cx, cy) for cx, cy in corners)
        else:
            far = 0

        # Lookahead vs what opponent might do: assume opponent moves greedily too
        # If we are pursuer, opponent is evader -> it will try to maximize distance from us.
        # If we are evader, opponent is pursuer -> it will try to minimize distance to us.
        # Approximate by evaluating our next-state after opponent's best greedy response.
        # (We don't know their role, so infer from our role.)
        opp_target_dxdy = []
        if is_pursuer:
            # opponent likely maximizes cheb(opp_next, self_next)
            want_max = True
            base_x, base_y = ox, oy
            ref_x, ref_y = x1, y1
        else:
            # opponent likely minimizes cheb(opp_next, self_next)
            want_max = False
            base_x, base_y = ox, oy
            ref_x, ref_y = x1, y1

        opp_best = None
        opp_best_val = None
        for odx, ody in dirs:
            ox1, oy1 = step(base_x, base_y, odx, ody)
            dist = cheb(ox1, oy1, ref_x, ref_y)
            val = dist
            if opp_best is None:
                opp_best, opp_best_val = (odx, ody), val
            else:
                if want_max and val > opp_best_val:
                    opp_best, opp_best_val = (odx, ody), val
                elif (not want_max) and val < opp_best_val:
                    opp_best, opp_best_val = (odx, ody), val

        odx, ody = opp_best if opp_best is not None else (0, 0)
        ox2, oy2 = step(ox, oy, odx, ody)
        d2 = cheb(x1, y1, ox2, oy2)

        # Final heuristic score
        # Add tiny tie-break using movement direction parity with position for determinism.
        tie = ((x1 + y1 + dx * 3 + dy * 5) % 7) * 1e-6
        if is_pursuer:
            score = (-d2, d1 * 0.0 + far + tie)  # prefer smaller d2
        else:
            score = (d2, far, tie)  # prefer larger d2 then far corner

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]