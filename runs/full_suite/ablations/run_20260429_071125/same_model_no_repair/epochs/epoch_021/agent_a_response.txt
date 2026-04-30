def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def safe(x, y):
        if not inb(x, y) or (x, y) in occ:
            return -10**9
        pen = 0
        # Strong penalty for moves that put us adjacent to obstacles
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in occ:
                    pen += 6 if (ax == 0 or ay == 0) else 4
        return -pen

    if not resources:
        return [0, 0]

    # Pick the resource where we maximize distance advantage: (opp_dist - our_dist)
    # Tie-break deterministically by closer overall and then lexicographic.
    best_res = None
    best_adv = -10**18
    for rx, ry in resources:
        if (rx, ry) in occ:
            continue
        our_d = dist(sx, sy, rx, ry)
        opp_d = dist(ox, oy, rx, ry)
        adv = opp_d - our_d
        if adv > best_adv:
            best_adv = adv
            best_res = (rx, ry)
        elif adv == best_adv and best_res is not None:
            cur_sum = our_d + opp_d
            best_sum = dist(sx, sy, best_res[0], best_res[1]) + dist(ox, oy, best_res[0], best_res[1])
            if cur_sum < best_sum or (cur_sum == best_sum and (rx, ry) < best_res):
                best_res = (rx, ry)

    # If no clear advantage, reduce damage: move toward a resource that is closest to us,
    # while increasing distance from opponent.
    focus_mode = (best_adv >= 2)
    if not focus_mode:
        best_res = min(
            [(rx, ry) for (rx, ry) in resources if (rx, ry) not in occ] or [(sx, sy)],
            key=lambda r: (dist(sx, sy, r[0], r[1]), r[0], r[1])
        )

    tx, ty = best_res
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        ns = safe(nx, ny)
        if ns < -10**8:
            continue

        d_to = dist(nx, ny, tx, ty)
        opp_to = dist(ox, oy, tx, ty)
        my_d = dist(nx, ny, tx, ty)

        # Primary: keep/establish advantage on the focused resource.
        adv = opp_to - my_d
        score = ns + (adv * 10)

        # Secondary: if chasing and we might be behind, prefer moves that reduce our distance gap.
        if focus_mode:
            cur_my_d = dist(sx, sy, tx, ty)
            cur_adv = dist(ox, oy, tx, ty) - cur_my_d
            score += (cur_my_d - my_d) * 3
        else:
            # Defensive/redistribution: move away from opponent while progressing.
            score += (dist(nx, ny, ox, oy) - dist(sx, sy, ox, oy)) * 2
            score += (-d_to)  # go toward target even in defensive mode

        # Deterministic tie-break: prefer closer to target, then lexicographic move.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if dist(nx, ny, tx, ty) < dist(sx + best_move[0], sy + best_move[1], tx, ty):
                best_move = (dx, dy)
            elif dist(nx