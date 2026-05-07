def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res = resources
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            val = -10**15
        else:
            # Find the most "contested" resource near us (small self distance).
            # Then use both players' distances to that resource to deny.
            self_near = 10**9
            opp_at_self_near = 10**9
            for rx, ry in res:
                sd = abs(rx - nx) + abs(ry - ny)
                if sd < self_near:
                    self_near = sd
                    opp_at_self_near = abs(rx - ox) + abs(ry - oy)
            # Global best distances from both sides (for shaping).
            self_min = min(abs(rx - nx) + abs(ry - ny) for rx, ry in res)
            opp_min = min(abs(rx - ox) + abs(ry - oy) for rx, ry in res)

            # Deny term: if opponent is relatively far from the resource we are closest to, that's good.
            deny = (opp_at_self_near - self_near)
            # Progress term: reduce our distance to resources.
            progress = -self_min
            # Additional pressure: prefer moves that also increase opponent's overall difficulty.
            opp_pressure = (opp_min - self_min)

            # Small tie-break to avoid obstacles adjacency stalls.
            adj_obs = 0
            for ax, ay in [(nx+1, ny), (nx-1, ny), (nx, ny+1), (nx, ny-1)]:
                if inb(ax, ay) and (ax, ay) in obs:
                    adj_obs += 1

            val = 50 * deny + 3 * progress + 1.5 * opp_pressure - 2 * adj_obs

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move