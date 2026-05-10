def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Assume opponent greedily minimizes our distance (pursuit).
    best_score = -1
    best = (0, 0)
    our_candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        our_candidates.append((dx, dy, nx, ny))

    for dx, dy, nx, ny in our_candidates:
        # opponent move that minimizes distance to our new position
        best_opp_d = 10**9
        opp_choices = []
        for odx, ody in moves:
            mx, my = ox + odx, oy + ody
            if not free(mx, my):
                mx, my = ox, oy
            d = cheb((mx, my), (nx, ny))
            if d < best_opp_d:
                best_opp_d = d
                opp_choices = [(odx, ody, mx, my)]
            elif d == best_opp_d:
                opp_choices.append((odx, ody, mx, my))
        # deterministic: smallest (odx, ody)
        odx, ody, mx, my = min(opp_choices, key=lambda t: (t[0], t[1]))
        # final evaluation: maximize resulting distance, and prefer not moving into corner-adjacent obstacles (implicit via legality)
        score = best_opp_d
        # If immediate capture possible (score==0), strongly avoid by adding tiny bias to staying away further.
        if score == 0:
            score = -1_000_000
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]