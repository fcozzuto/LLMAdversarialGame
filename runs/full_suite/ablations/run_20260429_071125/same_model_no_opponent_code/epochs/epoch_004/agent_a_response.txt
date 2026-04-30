def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation["obstacles"]}
    resources = [tuple(p) for p in observation["resources"]]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if (x, y) in obstacles:
        return [0, 0]

    # Competitive target: prefer resources where we are not behind, otherwise closest overall.
    targets = []
    for r in resources:
        myd = cheb((x, y), r)
        opd = cheb((ox, oy), r)
        score = (0 if myd <= opd else 1, myd, -opd, r)
        targets.append(score)
    targets.sort(key=lambda t: (t[0], t[1], t[2]))
    target_list = [t[3] for t in targets[:4]] if len(targets) >= 1 else []

    # If no resources, drift to center.
    if not target_list:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, (0, 0))
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                d = cheb((nx, ny), (cx, cy))
                if d < best[0]:
                    best = (d, (dx, dy))
        return [best[1][0], best[1][1]]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate moves against the top targets.
        val = 0.0
        for r in target_list:
            myd2 = cheb((nx, ny), r)
            opd2 = cheb((ox, oy), r)

            # Primary: get closer to the resource.
            val += 12.0 / (1 + myd2)

            # Secondary: if we can beat opponent on this resource, reward strongly.
            if myd2 <= opd2:
                val += 25.0 / (1 + myd2)

            # If opponent is currently closer, attempt to interfere by moving toward "contested" approach.
            if myd2 > opd2:
                # Push to reduce the opponent's advantage relative to r after our move (approx: our progress).
                val -= 10.0 / (1 + myd2) * (1 + (myd2 - opd2))

            # Micro-blocking: prefer moves that reduce distance to the square that would be closest to us-to-r.
            # Approx: prefer advancing along gradient toward r.
            cur_grad = cheb((nx, ny), r) - cheb((x, y), r)
            val -= 1.5 * cur_grad

        # Tie-break: prefer not moving away from any of our immediate top targets.
        for r in target_list[:1]:
            if cheb((nx, ny), r) < cheb((x, y), r):
                val += 0.5

        # Tie-break 2: keep within bounds and avoid obstacles already ensured; slight preference for staying if very close.
        if (nx, ny) == (x, y):
            val += 0.01

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]