def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in role) or ("hunter" in role) or ("seeker" in role)
    is_evader = ("evader" in role) or ("runner" in role) or ("fugitive" in role)
    if not (is_pursuer or is_evader):
        is_pursuer = True
    toward = is_pursuer

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def val_after(nsx, nsy, nox, noy):
        dx, dy = nsx - nox, nsy - noy
        return dx * dx + dy * dy

    best = (0, 0)
    best_val = -10**18 if toward else 10**18

    for mdx, mdy in deltas:
        nsx, nsy = sx + mdx, sy + mdy
        if not free(nsx, nsy):
            continue
        worst_for_us = 10**18 if toward else -10**18
        for odx, ody in deltas:
            nox, noy = ox + odx, oy + ody
            if not free(nox, noy):
                nox, noy = ox, oy
            d = val_after(nsx, nsy, nox, noy)
            if toward:
                if d < worst_for_us:
                    worst_for_us = d
            else:
                if d > worst_for_us:
                    worst_for_us = d
        if toward:
            if worst_for_us > best_val or (worst_for_us == best_val and (mdx, mdy) < best):
                best_val, best = worst_for_us, (mdx, mdy)
        else:
            if worst_for_us < best_val or (worst_for_us == best_val and (mdx, mdy) < best):
                best_val, best = worst_for_us, (mdx, mdy)

    return [int(best[0]), int(best[1])]