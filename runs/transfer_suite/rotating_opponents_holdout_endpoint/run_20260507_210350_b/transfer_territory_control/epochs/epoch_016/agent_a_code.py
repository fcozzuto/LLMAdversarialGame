def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (sx, sy))
    ox, oy = int(ox), int(oy)

    def to_set(lst):
        s = set()
        for p in (lst or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                try:
                    x, y = int(x), int(y)
                except:
                    continue
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    self_t = to_set(observation.get("self_territory"))
    opp_t = to_set(observation.get("opponent_territory"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_sc = -10**18
    best_mv = (0, 0)

    # Deterministic tie-break: fixed move order; only update on strictly better score.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        sc = 0

        # Territory pressure: prioritize flipping opponent cells, then taking unclaimed.
        if (nx, ny) in opp_t:
            sc += 1000
            # Prefer reaching opponent while on the way.
            sc += 10 * (-(nx - ox) * (nx - ox) - (ny - oy) * (ny - oy)) / 10.0
        elif (nx, ny) in unclaimed:
            sc += 120
        elif (nx, ny) in self_t:
            sc += 20
        else:
            sc += 5

        # Push along the vector from us to opponent.
        sc += -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) * 0.01

        # Center slight preference (reduces getting corner-trapped by edge-claim behavior).
        sc += -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.002

        # If resources exist, lightly bias toward them (even though resources per game is 0, harmless).
        if resources:
            if (nx, ny) in resources:
                sc += 200
            else:
                # Manhattan distance approximation to nearest resource.
                md = 10**9
                for rx, ry in resources:
                    d = abs(nx - rx) + abs(ny - ry)
                    if d < md:
                        md = d
                sc += -md * 0.5

        if sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]