def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Strategic change: prioritize resources we can contest (self not farther), else flank to least-contested
    # Use deterministic tie-break with resource ordering.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        contest = do - ds  # positive means we are closer/equal
        # Flank bias: prefer resources farther from opponent when contest is small/negative
        flank = cheb(ox, oy, rx, ry)
        # Deterministic key: prefer contest, then smaller ds, then larger flank, then coordinate
        key = (0 if contest >= 0 else 1, -contest, ds, -flank, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    # Move selection: greedy toward target with obstacle-avoidance and anti-lure term (avoid giving opponent the direct line)
    best_m = (0, 0)
    best_m_key = None
    do_t = cheb(ox, oy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ns_t = cheb(nx, ny, tx, ty)

        # Anti-lure: if opponent also can get closer from its current position, avoid moves that keep us behind.
        # Use local proxy: compare ns_t with current ds and how much it changes.
        ds_now = cheb(sx, sy, tx, ty)
        opp_closer = (cheb(ox, oy, tx, ty) < do_t)  # normally false since do_t is current, but kept harmless
        gain = ds_now - ns_t  # positive is good
        opp_race = ns_t - do_t  # smaller is better

        m_key = (-gain, opp_race, ns_t, nx, ny)
        if best_m_key is None or m_key < best_m_key:
            best_m_key = m_key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]