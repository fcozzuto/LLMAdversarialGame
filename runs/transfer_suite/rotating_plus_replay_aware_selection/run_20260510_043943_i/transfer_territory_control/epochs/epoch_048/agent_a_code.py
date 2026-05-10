def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set()
    for p in observation.get("self_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_t.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2
    opp_dist = abs(ox - sx) + abs(oy - sy)

    def neigh(x, y, s):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in s:
                    return True
        return False

    best = (-(10**9), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        score = 0

        if cell in self_t:
            score += 1
        elif cell in unclaimed:
            score += 6
            if neigh(nx, ny, self_t):
                score += 3
        elif cell in opp_t:
            score += 4
            if neigh(nx, ny, self_t):
                score += 2

        if neigh(nx, ny, opp_t):
            score -= 2  # avoid walking into their active edge unless capturing

        score += 0.1 * (-(abs(nx - cx) + abs(ny - cy)))
        nd = abs(ox - nx) + abs(oy - ny)
        score += 0.15 * (-(nd) if nd < opp_dist else 0)

        # deterministic tie-breaker: prefer moving away from previous (none), then lexicographic by dx,dy
        cand = (score, -dx, -dy)
        if cand > best:
            best = cand

    return [int(best[1] * -1), int(best[2] * -1)]