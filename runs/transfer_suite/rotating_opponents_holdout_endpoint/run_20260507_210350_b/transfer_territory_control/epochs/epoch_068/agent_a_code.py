def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dxdy = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_pos = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adjacent_to_opp(x, y):
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                if a == 0 and b == 0:
                    continue
                nx, ny = x + a, y + b
                if (nx, ny) in oppT:
                    return True
        return False

    best = [0, 0]
    best_score = -10**18
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in dxdy:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Primary objective: steal/claim where it matters (opp territory first).
        if (nx, ny) in oppT:
            val = 2000
        elif (nx, ny) in unclaimed:
            val = 350
        elif (nx, ny) in selfT:
            val = 50
        else:
            val = 120  # fallback for any cell not listed as territory/unclaimed

        # Tactical shaping: move toward opponent position while keeping momentum near their edge.
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        dist_curr = abs(sx - ox) + abs(sy - oy)
        momentum = (dist_curr - dist_to_opp) * 6  # prefer steps reducing distance

        edge_bonus = 180 if adjacent_to_opp(nx, ny) else 0

        # Soft discouragement of wandering far from center (helps vs edge-only opponents).
        center_pen = int(abs(nx - cx) + abs(ny - cy)) * 2

        score = val + momentum + edge_bonus - center_pen

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]