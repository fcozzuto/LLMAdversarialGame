def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Intercept-ish: move toward the most central relative to opponent.
        best = (-10**9, 0, 0, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            # Prefer increasing distance from opponent (deny) while staying mobile.
            # Secondary: minimize our distance to opponent's location's Chebyshev center-ish.
            score = (-v, nx, ny)
            if score > (best[0], best[1], best[2]):
                best = (score[0], score[1], score[2], dx, dy)
        return [best[3], best[4]]

    # Choose a move that maximizes our advantage to a contested resource,
    # but also reduces opponent's relative advantage after our move.
    best = (-10**18, 10**9, 10**9, 0, 0)  # primary, my_dist, opp_dist, dx, dy
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        # Evaluate the best contested resource for us under this move.
        best_adv = -10**18
        best_my = 10**9
        best_opp = 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d  # positive means we are closer (or equally close)
            # Extra bias: avoid only-slight wins where opponent is already much closer.
            # (Resource_denier: opponent will contest/steal if slightly favorable.)
            if adv > best_adv or (adv == best_adv and (my_d < best_my or (my_d == best_my and opp_d < best_opp))):
                best_adv, best_my, best_opp = adv, my_d, opp_d

        # Secondary tie-break over moves: prefer smaller distance to the chosen contested target;
        # then lexicographic move ordering for determinism.
        move_score = (best_adv, -best_opp, -best_my)  # maximize best_adv; then reduce opponent/our distances via signs
        cand = (move_score[0], best_my, best_opp, nx, ny)
        if cand[0] > best[0] or (cand[0] == best[0] and (cand[1], cand[2], dx, dy) < (best[1], best[2], best[3], best[4])):
            best = (cand[0], cand[1], cand[2], dx, dy)

    return [best[3], best[4]]