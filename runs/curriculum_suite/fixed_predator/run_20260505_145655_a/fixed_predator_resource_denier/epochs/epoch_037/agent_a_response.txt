def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_advantage(x, y, rx, ry):
        selfd = abs(x - rx) + abs(y - ry)
        oppd = abs(ox - rx) + abs(oy - ry)
        return (oppd - selfd), -selfd

    def pick_target(x, y):
        # If we're not leading anywhere, switch to the resource where we most reduce opponent lead (denial).
        bestLead = None
        bestRed = None
        for rx, ry in resources:
            dself = abs(x - rx) + abs(y - ry)
            dopp = abs(ox - rx) + abs(oy - ry)
            adv = dopp - dself
            if bestLead is None or adv > bestLead[0]:
                bestLead = (adv, -dself, rx, ry)
            # "reduce opponent advantage" = smaller positive adv, or larger negative adv
            red = abs(max(0, adv))  # only penalize when opponent is ahead
            if bestRed is None or red < bestRed[0] or (red == bestRed[0] and dself < bestRed[1]):
                bestRed = (red, dself, rx, ry)
        if bestLead[0] >= 0:
            return bestLead[2], bestLead[3], True  # leading somewhere
        return bestRed[2], bestRed[3], False

    tx, ty, leading = pick_target(sx, sy)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # One-step lookahead: assume we keep greedy toward the best target from next position.
        ntx, nty, nleading = pick_target(nx, ny)

        # Evaluate: try to maximize (opponent_distance - our_distance) to target.
        selfd = abs(nx - ntx) + abs(ny - nty)
        oppd = abs(ox - ntx) + abs(oy - nty)
        adv = oppd - selfd

        # Additional pressure: prefer moves that reduce our distance while not getting worse if opponent is closer.
        dist_focus = -selfd
        # If opponent is ahead on that same cell, prioritize minimizing their advantage.
        if adv > 0:
            deny = -adv
        else:
            deny = adv * 0.5

        # Slight preference to approach any resource where we can beat opponent (to avoid tunnel vision).
        best_any = None
        for rx, ry in resources:
            dself = abs(nx - rx) + abs(ny - ry)
            dopt = abs(ox - rx) + abs(oy - ry)
            a = dopt - dself
            if best_any is None or a > best_any:
                best_any = a
        multi = best_any

        # Tie-break deterministically by heading roughly toward target.
        htb = (1 if ntx > nx else -1 if ntx < nx else 0, 1 if nty > ny else -1 if nty < ny else 0)
        head = (dx == htb[0]) + (dy == htb[1])

        sc = 6.0 * adv + 2.0 * dist_focus + 3.0 * deny + 1.5 * multi + 0.1 * head
        if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
            best = (sc, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]