def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj4(x, y):
        return [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]

    candidates = []
    if self_terr and unclaimed:
        for (cx, cy) in unclaimed:
            if any((ax, ay) in self_terr for (ax, ay) in adj4(cx, cy)):
                candidates.append((cx, cy))
    if not candidates:
        candidates = list(unclaimed) if unclaimed else []

    # Fallback: head to a nearby unclaimed, otherwise retreat toward center-ish
    if not candidates:
        tx, ty = w // 2, h // 2
    else:
        # Prefer cells that are closer to opponent frontline relative to us (expand while limiting flips)
        best_t = None
        best_k = 10**18
        for (cx, cy) in candidates:
            d_to_us = abs(cx - sx) + abs(cy - sy)
            d_to_opp = abs(cx - ox) + abs(cy - oy)
            # Lower is better: closer to us, but also far from being "too far" behind while avoiding being deep in opponent area
            k = d_to_us * 3 + (w + h - d_to_opp)
            if k < best_k:
                best_k = k
                best_t = (cx, cy)
        tx, ty = best_t

    best_move = (0, 0)
    best_sc = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in unclaimed:
            sc += 900
        if (nx, ny) in self_terr:
            sc -= 10
        if (nx, ny) in opp_terr:
            sc -= 2000  # flipping is allowed, but it's usually losing territory under pursuit

        # Main objective: get closer to chosen target
        d_now = abs(nx - tx) + abs(ny - ty)
        sc -= d_now * 12

        # Keep pressure near our territory edge / avoid opening into opponent
        if self_terr:
            near_own = sum(1 for (ax, ay) in adj4(nx, ny) if (ax, ay) in self_terr)
            sc += near_own * 25
        if opp_terr:
            near_opp = sum(1 for (ax, ay) in adj4(nx, ny) if (ax, ay) in opp_terr)
            sc -= near_opp * 40

        # Discourage moving into immediate opponent proximity too aggressively
        d_opp = max(0, abs(nx - ox) + abs(ny - oy))
        sc += (d_opp) * 2

        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]