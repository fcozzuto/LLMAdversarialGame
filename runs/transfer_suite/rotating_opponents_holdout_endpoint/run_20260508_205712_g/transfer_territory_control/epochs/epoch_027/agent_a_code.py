def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    resources = set((int(x), int(y)) for x, y in (observation.get("resources") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Distance helper
    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = (0, 0, -10**18)
    d_to_opp = cheb_dist(sx, sy, ox, oy)
    opp_count = int(observation.get("opponent_territory_count", 0) or 0)
    my_count = int(observation.get("self_territory_count", 0) or 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        # Territory incentives
        if (nx, ny) in resources:
            score += 60
        if (nx, ny) in unclaimed:
            score += 35
        if (nx, ny) in opp_terr:
            # Counterclaim when ahead, otherwise be more cautious
            score += 22 if my_count >= opp_count else 10

        # Avoid getting too close to opponent (they can counterclaim back)
        dnow = cheb_dist(nx, ny, ox, oy)
        if dnow <= 1:
            score -= 55
        elif dnow == 2:
            score -= 18
        else:
            score += 6 * (dnow - 2)

        # Prefer moves that progress away from edges only slightly (territory is best when stable)
        edge_pen = 0
        if nx == 0 or nx == w - 1:
            edge_pen += 2
        if ny == 0 or ny == h - 1:
            edge_pen += 2
        score -= edge_pen

        # If currently far, reduce distance to nearest unclaimed-ish direction using rough target: closest unclaimed by manhattan if few
        if unclaimed:
            # Sample a few closest unclaimed deterministically around current region
            # (avoid full search for speed; but still based on observation)
            closest = None
            best_m = 10**9
            count_checked = 0
            for tx, ty in unclaimed:
                m = abs(nx - tx) + abs(ny - ty)
                if m < best_m:
                    best_m = m
                    closest = (tx, ty)
                count_checked += 1
                if count_checked >= 6:
                    break
            if closest is not None:
                score += max(0, 12 - best_m)

        # Small tie-break: deterministic preference ordering based on dx,dy
        if (dx, dy) == (0, 0):
            score -= 2
        score -= 0.1 * cheb_dist(nx, ny, sx, sy)
        score += 0.5 * (d_to_opp - dnow)

        if score > best[2]:
            best = (dx, dy, score)

    return [int(best[0]), int(best[1])]