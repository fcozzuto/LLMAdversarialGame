def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        # Deterministic: sweep toward a corner along a safe-ish axis
        corners = [(w - 1, 0), (w - 1, h - 1), (0, h - 1), (0, 0)]
        cx, cy = corners[(observation.get("turn_index", 0) or 0) % 4]
        tx, ty = cx, cy
    else:
        # Choose a resource where we're relatively advantaged; break ties deterministically by position.
        best = None
        for rx, ry in resources:
            sd = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            # If opponent is closer, we heavily penalize that target; otherwise reward.
            score = (sd - od) - 0.15 * (sd + od)
            score += (0.0 if rx % 2 == 0 else 0.02) + (0.0 if ry % 2 == 0 else 0.01)
            cand = (score, rx, ry)
            if best is None or cand < best:
                best = cand
        _, tx, ty = best

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # If the direct move is blocked, try alternative deterministic step toward the target.
    nx = sx + dx
    ny = sy + dy
    if (nx, ny) in obstacles:
        options = []
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                if abs(adx) > 1 or abs(ady) > 1:
                    continue
                if sx + adx < 0 or sx + adx >= w or sy + ady < 0 or sy + ady >= h:
                    continue
                if (sx + adx, sy + ady) in obstacles:
                    continue
                # prefer moves that reduce Manhattan distance to target
                nd = abs(tx - (sx + adx)) + abs(ty - (sy + ady))
                od = abs(tx - sx) + abs(ty - sy)
                options.append((nd, -((sx + adx) % 2), -((sy + ady) % 2), adx, ady, od - nd))
        options.sort()
        if options:
            adx, ady = options[0][3], options[0][4]
            return [int(adx), int(ady)]
        return [0, 0]

    return [int(dx), int(dy)]