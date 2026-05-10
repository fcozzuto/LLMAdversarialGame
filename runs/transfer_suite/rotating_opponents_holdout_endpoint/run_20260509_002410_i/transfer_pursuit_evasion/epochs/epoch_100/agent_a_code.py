def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or (role == "pursuer")

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    turn = int(observation.get("turn_index") or 0)

    # Directional bias for determinism: alternate preference order by turn parity
    pref = moves if (turn & 1) == 0 else list(reversed(moves))

    best = None
    best_val = None
    best_tie = None

    # Simple opponent "direct pursuit" prediction: opponent will reduce Chebyshev distance (avoiding obstacles if needed)
    def predict_opp_step():
        if pursuer:
            # opponent is evader: we still need some guess; assume it tries to increase distance
            target_sign = -1
        else:
            target_sign = 1
        bestm = None
        bestd = None
        for mdx, mdy in pref:
            nx, ny = ox + mdx, oy + mdy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, sx, sy)
            score = target_sign * d
            if bestm is None or score > best_val2:
                bestm = (mdx, mdy)
                best_val2 = score
        return bestm or (0, 0)

    opp_dx, opp_dy = predict_opp_step()

    # If we are evader, also avoid moving into where opponent would be closer next
    for mdx, mdy in pref:
        nx, ny = sx + mdx, sy + mdy
        if not inside(nx, ny):
            continue

        d_now = cheb(nx, ny, ox, oy)
        # Predicted next distance after opponent makes its direct move
        d_next = cheb(nx, ny, ox + opp_dx, oy + opp_dy)

        # Obstacle pressure: prefer staying farther from nearby obstacles
        obs_pen = 0
        for (ex, ey) in obstacles:
            dd = cheb(nx, ny, ex, ey)
            if dd == 0:
                obs_pen = 10
                break
            if dd == 1:
                obs_pen += 2

        if pursuer:
            val = -d_now * 10 + -d_next * 5 - obs_pen
            tie = (d_now, d_next, mdx, mdy)
            better = (best_val is None) or (val > best_val) or (val == best_val and tie < best_tie)
        else:
            val = d_now * 10 + d_next * 5 - obs_pen
            tie = (-d_now, -d_next, mdx, mdy)
            better = (best_val is None) or (val > best_val) or (val == best_val and tie < best_tie)

        if better:
            best_val = val
            best_tie = tie
            best = (mdx, mdy)

    return [int(best[0] if best else 0), int(best[1] if best else 0)]