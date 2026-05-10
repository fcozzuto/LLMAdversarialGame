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
    for b in (observation.get("obstacles") or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def near_block(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obs:
                    c += 1
        return c

    best = None
    best_score = -10**18 if toward else 10**18
    curd = dist2(sx, sy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dist2(nx, ny)
        dchange = nd - curd
        # Prefer decreasing distance if pursuer, increasing if evader
        progress = (-dchange) if toward else (dchange)
        # Wall/obstacle navigation: avoid getting too tightly surrounded; but allow sliding
        nb = near_block(nx, ny)
        # Bias towards matching opponent relative direction to reduce diagonal "wobble"
        sxg = 0 if ox == nx else (1 if ox > nx else -1)
        syg = 0 if oy == ny else (1 if oy > ny else -1)
        align = 0 if (sxg == 0 and syg == 0) else (abs((dx != 0) and (sxg != 0)) + abs((dy != 0) and (syg != 0)))
        score = (progress * 10) + (-nb * (3 if toward else -3)) + (align if toward else -align)
        # Deterministic tie-break: lexicographic on move
        if best is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]