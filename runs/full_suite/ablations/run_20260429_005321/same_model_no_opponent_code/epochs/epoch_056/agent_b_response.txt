def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    ti = observation.get("turn_index", 0)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            cands.append((dx, dy))

    if not cands:
        return [0, 0]

    opp_dist = abs(sx - ox) + abs(sy - oy)
    defensive = 1 if opp_dist <= 4 else 0
    best = None
    best_val = -10**18

    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy

        if resources:
            # Prefer the closest reachable resource; reward capturing.
            mind = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < mind:
                    mind = d
            resource_val = -mind
        else:
            resource_val = 0

        # Defensive / offensive bias: if opponent is close, try to increase distance.
        d_opp = abs(nx - ox) + abs(ny - oy)
        defend_val = d_opp if defensive else 0

        # Break ties deterministically toward a quadrant (based on turn index).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.01

        # Small deterministic oscillation to avoid deadlocks.
        osc = 0.001 * ((nx + 2 * ny + ti) % 7)

        val = resource_val + defend_val + center_bias + osc
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]