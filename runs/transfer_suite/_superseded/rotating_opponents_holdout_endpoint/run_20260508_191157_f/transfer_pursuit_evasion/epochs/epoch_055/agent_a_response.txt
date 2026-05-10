def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(x, lo, hi):
        if x < lo: return lo
        if x > hi: return hi
        return x

    # Heuristic target:
    # - Evader: maximize distance from pursuer (opponent).
    # - Pursuer: go to the cell "past" the opponent away from us, so we catch zigzags.
    if is_evader:
        tx, ty = ox, oy
    else:
        stepx = 0 if ox == sx else (1 if ox > sx else -1)
        stepy = 0 if oy == sy else (1 if oy > sy else -1)
        tx = clamp(ox + stepx, 0, w - 1)
        ty = clamp(oy + stepy, 0, h - 1)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Immediate win check (capture when same cell; capture radius 0)
        if (not is_evader) and (nx == ox and ny == oy):
            score = 10**9
        elif is_evader and (nx == ox and ny == oy):
            score = -10**9
        else:
            # Local obstacle pressure: slightly prefer safer cells to avoid getting boxed
            # by counting immediate blocked neighbors.
            blocked = 0
            for ax in (nx - 1, nx, nx + 1):
                if ax < 0 or ax >= w:
                    blocked += 1
                    continue
                for ay in (ny - 1, ny, ny + 1):
                    if ay < 0 or ay >= h:
                        blocked += 1
                        continue
                    if (ax, ay) in obstacles:
                        blocked += 1

            if is_evader:
                # Prefer large distance; also stay away from being in a tight obstacle neighborhood
                d1 = cheb(nx, ny, tx, ty)
                score = d1 * 100 - blocked
            else:
                # Prefer small distance to target; tie-break by reducing direct distance to opponent too
                d_to_target = cheb(nx, ny, tx, ty)
                d_to_op = cheb(nx, ny, ox, oy)
                score = -(d_to_target * 10 + d_to_op) * 100 - blocked

        if best is None:
            best, best_score = (dx, dy), score
        else:
            if (is_evader and score > best_score) or ((not is_evader) and score > best_score):
                best, best_score = (dx, dy), score
            # Deterministic tie-breaking: keep earlier move in the list (since we only update on '>')
    if best is None:
        return [0, 0]
    return [best[0], best[1]]