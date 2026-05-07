def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    def turns(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))

    # Deterministic tie-break: prefer progressing right/down then staying.
    def tie_key(dx, dy):
        return (-dx, -dy, 0 if (dx == 0 and dy == 0) else 1)

    best = None
    best_score = None

    rem = observation.get("remaining_resource_count", len(resources))
    urgency = 1.0 if rem <= 4 else 0.6 if rem <= 8 else 0.35
    closer_bonus = 0.15 * urgency

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        move_score = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ot = turns(ox, oy, rx, ry)
            st = turns(nsx, nsy, rx, ry)

            # Primary: how much earlier we arrive than opponent.
            lead = ot - st
            # Secondary: prefer earlier overall, and slightly prefer lower Manhattan-like distance to avoid dithering.
            dist = abs(rx - nsx) + abs(ry - nsy)

            if lead >= 0:
                s = 10**6 + (lead * 10) - (st * (1.0 + 2.0 * closer_bonus)) - dist * 0.01
            else:
                # Still consider resources we can potentially contest later, but strongly deprioritize being behind.
                s = (lead * 10) - (st * 2.0) - dist * 0.02

            # Small deterministic preference to reduce symmetry: aim for resources with "lower" coordinate sum when tied.
            s -= (rx + ry) * 0.0001
            if s > move_score:
                move_score = s

        # Add slight preference to avoid backtracking loops: favor moves that reduce distance to best target-ish point.
        # Use average of resource positions as a cheap steering target.
        ax = 0
        ay = 0
        k = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ax += rx
            ay += ry
            k += 1
            if k >= 6:
                break
        if k > 0:
            ax //= k
            ay //= k
            move_score += -(turns(nsx, nsy, ax, ay) * 0.05)

        if best_score is None or move_score > best_score or (move_score == best_score and tie_key(mdx, mdy) < tie_key(best[0], best[1])):
            best_score = move_score
            best = (mdx, mdy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]