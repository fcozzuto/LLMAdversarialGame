def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d_opp = cheb(nx, ny, ox, oy)
            center = abs(nx - cx) + abs(ny - cy)
            score = d_opp - 0.08 * center
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Opponent-denial strategy: contest the resource opponent is closest to.
    opp_close = None
    best_opp_d = None
    for r in resources:
        d = cheb(r[0], r[1], ox, oy)
        if best_opp_d is None or d < best_opp_d:
            best_opp_d = d
            opp_close = r

    best = (-10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        dS = cheb(nx, ny, opp_close[0], opp_close[1])
        dO = best_opp_d
        # Primary: maximize our advantage on the opponent's nearest resource.
        score = (dO - dS)

        # Secondary: if we can reach another resource that also threatens the opponent, reward it.
        # Use only top few resources by opponent distance for determinism and speed.
        scored = []
        for r in resources:
            scored.append((cheb(r[0], r[1], ox, oy), r))
        scored.sort(key=lambda t: t[0])
        topk = scored[:4]
        threat_gain = 0
        for od, r in topk:
            ds = cheb(nx, ny, r[0], r[1])
            threat_gain += 0.25 * (od - ds)
        score += threat_gain

        # Tertiary: keep moving toward center to avoid getting stuck.
        score -= 0.03 * (abs(nx - cx) + abs(ny - cy))

        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]