def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def best_for_pursuer():
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            # tie-break: prefer direct approach
            tie = (abs(dx) + abs(dy), -dx if ox < sx else dx if ox > sx else 0, -dy if oy < sy else dy if oy > sy else 0)
            cand = (dist, tie)
            if best is None or cand < best[0]:
                best = (cand, (dx, dy))
        return best[1] if best else [0, 0]

    def best_for_evader():
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            # tie-break: prefer keeping within bounds and not moving toward pursuer
            score = (dist, -abs(dx), -abs(dy), -dx * (ox - sx) if (ox - sx) != 0 else 0, -dy * (oy - sy) if (oy - sy) != 0 else 0)
            if best is None or score > best[0]:
                best = (score, (dx, dy))
        return best[1] if best else [0, 0]

    role = observation.get("self_role", "pursuer")
    if role == "pursuer":
        return best_for_pursuer()
    else:
        return best_for_evader()