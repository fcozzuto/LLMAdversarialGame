def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                self_t.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                opp_t.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                unclaimed.add((x, y))

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H:
                candidates.append((dx, dy, nx, ny))
    candidates.sort(key=lambda t: (t[0], t[1]))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = -10**9
    for dx, dy, nx, ny in candidates:
        if (nx, ny) in obstacles:
            continue

        base = 0
        if (nx, ny) in opp_t:
            base += 120  # flipping on entry
        elif (nx, ny) in unclaimed:
            base += 55
        elif (nx, ny) in self_t:
            base += 10
        else:
            base += 5  # likely already claimed by opponent? still safe fallback

        # Prefer closing distance to opponent while not overcommitting into obstacles
        chase = 12 * (man(sx, sy, ox, oy) - man(nx, ny, ox, oy))
        # Prefer staying away from edges late-ish to reduce being trapped
        edge_pen = -2 * (min(nx, W - 1 - nx) + min(ny, H - 1 - ny) == 0)
        # Slight preference to approach center for stable territory growth
        cx, cy = (W - 1) // 2, (H - 1) // 2
        center = 2 * (man(nx, ny, cx, cy) * -1)

        val = base + chase + edge_pen + center
        if val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]