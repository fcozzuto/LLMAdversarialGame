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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def min_obs_dist(x, y):
        if not obstacles:
            return 99
        md = 99
        for ox1, oy1 in obstacles:
            d = cheb(0, 0, x - ox1, y - oy1)
            if d < md:
                md = d
        return md

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    remaining = int(observation.get("remaining_resource_count") or len(resources))
    late = 1 if remaining <= 6 else 0
    k_away = 0.35 + (0.2 * (1 if late else 0))  # avoid hugging obstacles

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        md_obs = min_obs_dist(nx, ny)
        obs_pref = k_away * (md_obs if md_obs < 5 else 4)

        # Choose target that maximizes our advantage after this move.
        best_target_adv = -10**18
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            lead_now = do - ds  # positive means we are closer than opponent

            # If opponent is currently closer (lead_now negative), allow only if we can flip it.
            flip_bonus = 0
            if lead_now < 0:
                # how much we improve vs current self distance
                cur_s = cheb(sx, sy, tx, ty)
                improve = cur_s - ds
                if improve > 0:
                    flip_bonus = (3.0 if late else 1.5) * min(improve, 3)

            # Late game: stronger commitment to securing a nearby lead.
            commit = (2.0 if late else 1.0) * lead_now - 0.06 * ds
            val = commit + flip_bonus
            if val > best_target_adv:
                best_target_adv = val

        total = best_target_adv + obs_pref
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]