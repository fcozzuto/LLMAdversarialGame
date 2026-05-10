def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Prefer pushing toward nearest unclaimed "front", but only attack if it tightens our control boundary.
    opp_near = min((abs(sx-x)+abs(sy-y) for (x,y) in oppT), default=99)
    prefer_attack = (opp_near <= 3)  # if opponent is close, we sometimes flip to disrupt
    my_edge_adv = (edge_dist(sx, sy) <= edge_dist(ox, oy))

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0.0
        if (nx, ny) in selfT:
            sc += 0.6
        if (nx, ny) in unclaimed:
            sc += 6.0
        if (nx, ny) in oppT:
            sc += 7.0 if prefer_attack else 2.0

        # Boundary pressure: move to keep expanding our outer ring, avoid drifting inward.
        sc += (7 - edge_dist(nx, ny)) * 0.25

        # Create "frontline": reward moves that are adjacent to unclaimed cells.
        adj_unclaimed = 0
        for ddx, ddy in dirs:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in unclaimed:
                adj_unclaimed += 1
        sc += adj_unclaimed * 0.35

        # Defense: if stepping into opponent territory, ensure it's near our boundary or near our current territory edge.
        if (nx, ny) in oppT:
            adj_self = 0
            for ddx, ddy in dirs:
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in selfT:
                    adj_self += 1
            sc += (2.2 if adj_self >= 2 else 0.8)

        # Opponent proximity shaping: avoid giving them an easy next flip by keeping some distance when not attacking.
        d2opp = abs(nx - ox) + abs(ny - oy)
        if prefer_attack:
            sc += max(0, 4 - d2opp) * 0.35
        else:
            sc += max(0, d2opp - 2) * 0.12

        # If we are behind on edge (our edge more inward), prioritize moves with smaller edge_dist.
        if my_edge_adv:
            sc += (edge_dist(sx, sy) - edge_dist(nx, ny)) * 0.6

        # Avoid oscillation: discourage staying if we have a clear unclaimed adjacent.
        if dx == 0 and dy == 0:
            sc -= 1.2
        if (nx, ny) in selfT and (sx == nx and sy == ny):
            sc -= 0.2

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    # Ensure integers in {-1,0,1}
    return [int(best[0]), int(best[1])]