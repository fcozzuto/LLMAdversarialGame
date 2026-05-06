def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    def best_target_for(posx, posy):
        if not resources:
            return None, 10**9
        best = None
        bd = 10**9
        for rx, ry in resources:
            d = cheb(posx, posy, rx, ry)
            if d < bd:
                bd = d
                best = (rx, ry)
        return best, bd

    if not resources:
        # deterministic repositioning: move toward the center column/row opposite the opponent
        tx = w // 2 if ox < w // 2 else (w // 2 - 1 if w // 2 - 1 >= 0 else w // 2)
        ty = h // 2 if oy < h // 2 else (h // 2 - 1 if h // 2 - 1 >= 0 else h // 2)
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and cheb(nx, ny, ox, oy) > best[1]):
                best = (d, cheb(nx, ny, ox, oy), dx, dy)
        return [best[2], best[3]]

    # Evaluate each move by "who can reach a resource first" (tempo win), then tie-break by closeness.
    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        best_adv = -10**9
        best_dist = 10**9
        # Prefer taking a resource where we are closer (or at least not worse) than the opponent.
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self  # positive means tempo advantage
            if adv > best_adv or (adv == best_adv and d_self < best_dist):
                best_adv = adv
                best_dist = d_self

        # Extra tie-break: avoid stepping into immediate opponent proximity (resource denial pressure).
        opp_next_dist = cheb(nx, ny, ox, oy)
        score = (best_adv, -best_dist, opp_next_dist)

        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]