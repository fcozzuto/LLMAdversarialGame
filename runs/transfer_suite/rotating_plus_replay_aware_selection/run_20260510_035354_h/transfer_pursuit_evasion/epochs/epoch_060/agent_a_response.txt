def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    r = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in r) or ("chaser" in r) or ("hunter" in r) or ("catcher" in r)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)
    parity = t & 1

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y, a=ox, b=oy):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def corner_targets():
        # Alternate among far corners for more diversity
        if (ox + oy + parity) & 1:
            return [(w - 1, h - 1), (0, 0), (w - 1, 0), (0, h - 1)]
        return [(0, 0), (w - 1, h - 1), (0, h - 1), (w - 1, 0)]

    def obs_risk(x, y):
        if (x, y) in obs:
            return 10**9
        risk = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obs:
                    risk += 3
        # Slight bias to avoid being boxed near multiple obstacle-adjacent cells
        return risk

    best = None
    bestv = None
    targets = corner_targets()
    # If evader: aim away; if pursuer: aim closer
    # Also, when obstacles exist, add a light heuristic towards/away from a chosen corner.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        v = 0
        d = dist2(nx, ny)
        if pursuer:
            v += d * 10
            # Prefer reducing Chebyshev distance too (diagonal chase)
            v += max(abs(nx - ox), abs(ny - oy)) * 2
            # Avoid moving around obstacles only: risk penalty
            v += obs_risk(nx, ny) * 5
            # Micro-aim at opponent corner to avoid oscillation
            tx, ty = targets[(t + (ox & 1) + (oy & 1)) & 3]
            v += (max(abs(tx - nx), abs(ty - ny)) - max(abs(tx - ox), abs(ty - oy))) * 0.1
            score = -v
        else:
            v += d * 10
            # Prefer larger Chebyshev distance too
            v += max(abs(nx - ox), abs(ny - oy)) * 2
            v -= obs_risk(nx, ny) * 5
            # Aim towards farthest target corner (deterministic)
            tx, ty = targets[(t + (sx & 1) + (sy & 1)) & 3]
            v += max(abs(tx - nx), abs(ty - ny)) * 0.5
            score = v

        if best is None or score > bestv:
            bestv = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]