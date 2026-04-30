def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    nbrs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_from(start):
        dist = {}
        x0, y0 = start
        if (x0, y0) in obstacles:
            return dist
        dist[(x0, y0)] = 0
        q = [(x0, y0)]
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            d0 = dist[(x, y)] + 1
            for dx, dy in nbrs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) not in dist:
                    dist[(nx, ny)] = d0
                    q.append((nx, ny))
        return dist

    sd = bfs_from((sx, sy))
    od = bfs_from((ox, oy))

    # If we can grab something immediately, do it.
    best_now = None
    for r in resources:
        r = (r[0], r[1])
        if sd.get(r, 10**9) == 1 or sd.get(r, 10**9) == 0:
            best_now = r
            break
    if best_now is not None:
        rx, ry = best_now
        best_d = 10**9
        best = (0, 0)
        for dx, dy in nbrs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = sd.get((nx, ny), 10**9)
                if d < best_d:
                    best_d = d
                    best = (dx, dy)
        return [best[0], best[1]]

    # Choose target resource maximizing advantage (opponent farther than us), with preference for closeness.
    best_target = None
    best_score = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        sdv = sd.get((rx, ry), 10**9)
        odv = od.get((rx, ry), 10**9)
        if sdv == 10**9:
            continue
        # Advantage: larger means opponent is worse.
        adv = (odv - sdv)
        # Bias towards nearer targets, but don't go extremely far if opponent is also far.
        score = adv * 1000 - sdv * 10
        # Slightly prefer resources that remain reachable quickly for us.
        if odv == 10**9:
            score += 2000
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    # Step to neighbor that increases (opponent_dist - self_dist) while reducing self_dist to target.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in nbrs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ns = sd.get((nx, ny), 10**9)
        no = od.get((nx, ny), 10**9)
        ns_to_t = sd.get((tx, ty), 10**9)  # keep stable
        nd_target = sd.get((tx, ty), 10**9)  # placeholder stable; use chebyshev for local bias
        local_bias = max(abs(nx - tx), abs(ny - ty))
        cheb_opp = max(abs(ox - nx), abs(oy - ny))
        # Main: be closer to target than opponent is (via their distance to target).
        t_sd = sd.get((tx, ty), 10**9)
        t_od = od.get((tx, ty), 10**