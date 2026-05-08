def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    self_role = (observation.get("self_role") or "")
    i_am_pursuer = ("pursuer" in self_role.lower()) or (self_role.lower() == "pursuer")

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If pursuer: move to minimize worst-case next distance assuming evader can respond.
    # If evader: move to maximize worst-case next distance assuming pursuer can respond.
    best_val = None
    best_mv = (0, 0)

    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not inb(nsx, nsy):
            continue

        # Candidate evader/pursuer action set (only based on occupancy; deterministic evaluation)
        worst = None
        for odx, ody in moves:
            nox, noy = ox + odx, oy + ody
            if not inb(nox, noy):
                continue

            dist = cheb(nsx, nsy, nox, noy)
            if dist == 0:
                val = (10**9 if i_am_pursuer else -10**9)
            else:
                # Prefer immediate tactical improvements; use squared to sharpen.
                val = dist * dist

            # If we are pursuer, we want opponent response to be as bad for us as possible (maximize dist).
            # If we are evader, we want opponent response to be as bad for them as possible (maximize our survival => maximize dist).
            if i_am_pursuer:
                # opponent chooses after our move: worst for us is larger dist
                score = -val  # our preference: smaller dist => larger (less negative) score
                worst = score if worst is None else (worst if worst < score else score)
            else:
                # opponent is pursuer: worst for us is smaller dist; we want to maximize dist
                score = -val  # our preference: larger dist => more negative val? invert below for consistency
                # For evader, evaluate directly by dist^2 (bigger is better), so use val as dist^2
                worst = val if worst is None else (worst if worst > val else val)

        if i_am_pursuer:
            # worst is maximum of (-dist^2) over opponent actions => corresponds to minimum of dist^2
            # We want maximize (i.e., closest) => choose higher worst (closer)
            final_val = worst
            better = (best_val is None) or (final_val > best_val)
        else:
            # worst is maximum dist^2 over opponent actions (best evasion robustness)
            final_val = worst
            better = (best_val is None) or (final_val > best_val)

        if better:
            best_val = final_val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]