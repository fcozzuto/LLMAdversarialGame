def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    ox, oy = observation["opponent_position"]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**9, 0, 0)

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx*dx + dy*dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        # Territory flipping is enabled on entry
        gain = 0.0
        if (nx, ny) in opp_set:
            gain += 6.0 + 0.5 * dist(nx, ny, ox, oy) ** 0  # deterministic constant bump
        if (nx, ny) in unclaimed:
            gain += 3.5
        if (nx, ny) in my_set:
            gain += 1.0

        # Pressure toward/around opponent and center for "territory_center_claim" nemesis
        opp_adj = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (nx + ex, ny + ey) in opp_set:
                    opp_adj += 1
        gain += 0.8 * opp_adj

        # Avoid getting too close to opponent head while still pressuring
        d_opp = dist(nx, ny, ox, oy)
        gain += -0.002 * d_opp

        # Prefer expanding toward center lanes
        gain += -0.01 * dist(nx, ny, cx, cy)

        # Prefer moves that increase adjacency to unclaimed (cuts off growth)
        un_adj = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (nx + ex, ny + ey) in unclaimed:
                    un_adj += 1
        gain += 0.6 * un_adj

        if gain > best[0]:
            best = (gain, dx, dy)

    if best[0] == -10**9:
        return [0, 0]
    return [int(best[1]), int(best[2])]