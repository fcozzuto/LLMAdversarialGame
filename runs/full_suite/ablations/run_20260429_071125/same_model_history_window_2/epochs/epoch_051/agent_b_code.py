def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Strategy change: attack resources where opponent is closer (steal/deny),
    # but only if we can get closer this turn; else drift to best available advantage.
    best_move = None
    best_key = None
    for dx, dy, nx, ny in valid:
        my_dist_now = cheb(nx, ny, ox, oy)
        move_score = -10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Opponent pressure: how much closer opponent is to this resource.
            opp_press = d_opp - d_self  # positive => we are (relatively) closer now
            # Deny/steal focus: if opponent is currently closer to resource, prioritize denying.
            my_before = cheb(sx, sy, rx, ry)
            opp_before = cheb(ox, oy, rx, ry)
            opp_closer_now = 1 if opp_before < my_before else 0
            # If we can't beat opponent's current lead, still take a resource that improves our advantage.
            score = (25 * opp_closer_now + 6 * opp_press) - d_self
            # Safety: avoid moving too close to opponent while contesting.
            safety = 0
            if opp_closer_now:
                safety = min(10, my_dist_now) * 0.2
            score += safety
            # Deterministic tie-breaker uses resource coordinates.
            key = (score, -rx, -ry)
            if key > (move_score, -999999, -999999):
                move_score = key[0]
        # Final key for move selection:
        # Prefer highest move_score, then maximize distance-from-opponent when contesting,
        # then minimize distance to nearest resource.
        nearest_after = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        contest = 1 if min(cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry) for rx, ry in resources) > 0 else 0
        opp_dist = cheb(nx, ny, ox, oy)
        final_key = (move_score, contest * opp_dist, -nearest_after, dx, dy)
        if best_key is None or final_key > best_key:
            best_key = final_key
            best_move = [dx, dy]
    return best_move