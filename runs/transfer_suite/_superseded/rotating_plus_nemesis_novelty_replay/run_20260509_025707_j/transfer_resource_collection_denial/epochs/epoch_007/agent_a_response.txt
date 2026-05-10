def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    # Score next position: prefer stealing resources where we are closer, else approach the best stealable
    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Evaluate resources with a stronger "lead" heuristic and slight preference for safety (stay away from obstacles)
        lead_best = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - sd  # positive means we are closer after the move
            if lead_best is None or (lead, -sd) > (lead_best[0], lead_best[1]):
                lead_best = (lead, -sd, rx, ry)

        lead, neg_sd, tx, ty = lead_best

        # Tie-break: if lead is non-positive everywhere, move to reduce distance to the nearest resource overall
        near_self = min(man(nx, ny, rx, ry) for rx, ry in resources)
        near_opp = min(man(ox, oy, rx, ry) for rx, ry in resources)

        # Obstacle proximity penalty (deterministic and lightweight)
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                cx, cy = nx + ax, ny + ay
                if (cx, cy) in obstacles:
                    adj_pen += 1

        val = (lead, -near_self, -adj_pen, man(nx, ny, tx, ty) * -1, lead + (near_opp - near_self) * 0.1)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]