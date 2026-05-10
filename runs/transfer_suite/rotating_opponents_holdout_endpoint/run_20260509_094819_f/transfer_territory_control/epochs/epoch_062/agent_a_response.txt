def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) == 2)
    self_t = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) == 2)
    opp_t = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) == 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) == 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def neighbors_free(x, y):
        cnt = 0
        for ddx, ddy in dirs[:-1]:  # exclude one diagonal to keep deterministic variety; still fine
            nx, ny = x + ddx, y + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    def nearest_unclaimed_dist2(x, y):
        if not unclaimed:
            return (w * w + h * h)
        best = 10**9
        for tx, ty in unclaimed:
            dx, dy = tx - x, ty - y
            d = dx * dx + dy * dy
            if d < best:
                best = d
        return best

    best_move = [0, 0]
    best_score = -10**18
    x0, y0 = sx, sy
    for dx, dy in dirs:
        nx, ny = x0 + dx, y0 + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_t:
            base = 3
        elif (nx, ny) in unclaimed:
            base = 12
        elif (nx, ny) in opp_t:
            base = 9
        else:
            base = 1

        center_bonus = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.02
        frontier_bonus = 0
        for ddx, ddy in dirs[:4]:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in self_t:
                frontier_bonus = 1.2
                break

        dist2_un = nearest_unclaimed_dist2(nx, ny)
        unclaimed_bonus = 0 if dist2_un > 200 else (220 - dist2_un) * 0.03

        mobility = neighbors_free(nx, ny) * 0.25

        score = base + center_bonus + frontier_bonus + unclaimed_bonus + mobility
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move