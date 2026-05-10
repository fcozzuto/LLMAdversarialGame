def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    # Pick a target resource to maximize winning chances (distance advantage),
    # with a small bias toward being closer soon.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (od - sd, -sd, rx, ry)  # prefer biggest advantage, then closer
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Evaluate next move options locally; stay within bounds by clamping via engine behavior,
    # but we still avoid obvious obstacle collisions by penalizing them.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            hit = (nx, ny) in obs_set
            dist_to_target = abs(tx - nx) + abs(ty - ny)
            # Also reward moving toward any resource, but primarily target-driven.
            min_res_dist = 10**9
            for rx, ry in resources:
                d = abs(rx - nx) + abs(ry - ny)
                if d < min_res_dist:
                    min_res_dist = d
            # Opponent pressure: if we are approaching a tile where opponent can also race, prefer narrowing gap.
            self_future = abs(tx - nx) + abs(ty - ny)
            opp_future = abs(tx - ox) + abs(ty - oy)
            gap = opp_future - self_future
            # Deterministic scoring; higher is better.
            score = (gap * 100) - dist_to_target - (0 if hit else 0) - (50 if hit else 0) - min_res_dist * 0.2
            # Prefer not to stay still unless equal.
            if dx == 0 and dy == 0:
                score -= 0.5
            candidates.append((score, dx, dy))

    candidates.sort(key=lambda t: (t[0], -t[1], -t[2]), reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]