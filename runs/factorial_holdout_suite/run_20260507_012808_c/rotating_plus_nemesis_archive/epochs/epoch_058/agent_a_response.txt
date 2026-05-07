def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obs.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y): res.append((x, y))

    directions = [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)]
    best_move = [0, 0]
    best_val = -10**18

    if not res:
        return [0, 0]

    for dx, dy in directions:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Value: want resources we can reach sooner, and also avoid giving opponent advantage.
        min_d_opp = 10**9
        best_for_us = -10**18
        for rx, ry in res:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Encourage immediate collection and "safe races" where we are closer.
            immediate = 1 if (nx == rx and ny == ry) else 0
            val = immediate * 10**6 + (d_opp - d_self) * 100 - d_self
            if val > best_for_us:
                best_for_us = val
            if d_opp < min_d_opp:
                min_d_opp = d_opp

        # If opponent is extremely close to some resource, bias toward landing closer to any resource.
        fallback_pressure = -min_d_opp
        total = best_for_us + fallback_pressure

        # Tie-break deterministically by preferring less move distance from current.
        total -= cheb(nx, ny, sx, sy) * 1e-3

        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move