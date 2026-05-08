def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def adj_count(px, py):
        c = 0
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            if (px+dx, py+dy) in opp_t:
                c += 1
        return c

    # Bias target direction toward where we are likely to expand (toward opponent side).
    # If no unclaimed adjacent exists, fall back to closest unclaimed overall; else hover on border.
    adj_unclaimed = []
    if unclaimed:
        for ux, uy in unclaimed:
            if adj_count(ux, uy) > 0:
                adj_unclaimed.append((ux, uy))
    if adj_unclaimed:
        tx, ty = min(adj_unclaimed, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), p[0], p[1]))
    elif unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0]-sx)+abs(p[1]-sy), p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = (float("-inf"), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        a = adj_count(nx, ny)
        base = 0.0
        if (nx, ny) in opp_t:
            base += 4.0 + a * 1.0
        elif (nx, ny) in unclaimed:
            base += 2.5 + a * 2.0
        elif (nx, ny) in self_t:
            base += 0.6 + a * 0.3
        else:
            base += 0.2

        dist_now = abs(nx - tx) + abs(ny - ty)
        dist_cur = abs(sx - tx) + abs(sy - ty)
        progress = (dist_cur - dist_now) * 0.35

        edge = 0
        if nx in (0, w-1) or ny in (0, h-1):
            edge = 0.05  # slight determinism; avoid purely wall-hugging

        score = base + progress + edge
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]