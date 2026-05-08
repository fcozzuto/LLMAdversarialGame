def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        pts = observation.get(key) or []
        for p in pts:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    cx, cy = w // 2, h // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**18), 0, 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base value: claim/unclaim opp for flipping.
        score = 0.0
        if (nx, ny) in self_terr:
            score += 1.0
        if (nx, ny) in unclaimed:
            score += 3.0
        if (nx, ny) in resources:
            score += 7.0
        if (nx, ny) in opp_terr:
            score += 10.5

        # Progress toward center while keeping pressure on opponent.
        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        score += -0.03 * dist_center
        score += -0.02 * dist_to_opp

        # If near opponent, prioritize moves that grab contested cells.
        if dist_to_opp <= 3 and ((nx, ny) in opp_terr or (nx, ny) in unclaimed):
            score += 1.0

        # Mild preference to reduce immediate risk of opponent next-step capture.
        # Estimate: count how many of opponent's neighbor cells would be good targets.
        opp_best = 0
        for ddx, ddy in moves:
            ax, ay = ox + ddx, oy + ddy
            if not inb(ax, ay) or (ax, ay) in obstacles:
                continue
            if (ax, ay) in opp_terr:
                opp_best += 1
            if (ax, ay) in unclaimed:
                opp_best += 1
            if (ax, ay) in resources:
                opp_best += 1
            if (ax, ay) in self_terr:
                opp_best -= 0.5
        score += -0.05 * opp_best

        cand = (score, -dx * 100 - dy, dx, dy)
        if cand > best:
            best = cand

    # If all moves blocked, stay.
    if best[2] == 0 and best[3] == 0:
        return [0, 0]
    return [int(best[2]), int(best[3])]