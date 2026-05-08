def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_count = int(observation.get("self_territory_count") or 0)
    opp_count = int(observation.get("opponent_territory_count") or 0)

    unclaimed = [(int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or [])]
    oppT = [(int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or [])]

    cx, cy = w // 2, h // 2

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    prefer_flip = opp_count > self_count
    targets = unclaimed if unclaimed else []
    if not targets and oppT:
        targets = oppT

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if targets:
        best_t = None
        best_k = None
        for t in targets:
            if t in obstacles:
                continue
            # Prefer center and unclaimed; if behind, prefer opponent cells (flip on entry).
            k = dist(t, (cx, cy))
            if prefer_flip and t in oppT:
                k -= 5
            # Also avoid moving into opponent territory when we're ahead.
            if not prefer_flip and t in oppT:
                k += 5
            # Slight preference closer to us than opponent to reduce counterplay.
            k += (dist(t, (sx, sy)) - dist(t, (ox, oy))) * 0.2
            if best_k is None or k < best_k or (k == best_k and (t[0], t[1]) < (best_t[0], best_t[1])):
                best_k = k
                best_t = t
        target = best_t
    else:
        target = (cx, cy)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Score: move towards target; if flipping, boost opponent cells.
        val = -dist((nx, ny), target)
        if (nx, ny) in oppT and prefer_flip:
            val += 8
        if (nx, ny) in unclaimed:
            val += 6
        # Keep away from opponent position slightly.
        val -= 0.15 * dist((nx, ny), (ox, oy))
        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    if best_move == [0, 0]:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]