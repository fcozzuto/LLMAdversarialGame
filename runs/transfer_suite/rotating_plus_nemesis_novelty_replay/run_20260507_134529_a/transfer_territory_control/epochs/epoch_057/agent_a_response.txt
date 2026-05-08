def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        # Heuristic: contest center, avoid opponent proximity, and prioritize flipping/claiming.
        md_center = abs(nx - cx) + abs(ny - cy)
        md_opp = abs(nx - ox) + abs(ny - oy)
        score = 0.0
        score += -2.4 * md_center
        score += 1.3 * md_opp
        if (nx, ny) in opp_terr:
            score += 8.5  # flip on entry
        elif (nx, ny) in unclaimed:
            score += 2.2
        elif (nx, ny) in self_terr:
            score += 0.6
        # Prefer moving when it reduces center distance, slightly discouraging oscillation via opponent distance change
        score += 0.3 * (abs(sx - cx) + abs(sy - cy) - md_center)
        # Softly avoid stepping adjacent to obstacles (navigation safety)
        adj_obs = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in obstacles:
                adj_obs += 1
        score += -0.35 * adj_obs

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]