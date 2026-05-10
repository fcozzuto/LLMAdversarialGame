def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    unclaimed = observation.get("unclaimed_cells") or []
    un = set((p[0], p[1]) for p in unclaimed)

    candidates = []
    best = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            if un:
                if (nx, ny) in un:
                    score = 10**9
                else:
                    # greedy: prefer moves that reduce Manhattan distance to nearest unclaimed
                    md = 10**9
                    for ux, uy in un:
                        d = abs(nx - ux) + abs(ny - uy)
                        if d < md:
                            md = d
                    score = -md
            else:
                # fallback: head toward opponent if known, else stay toward center
                opp = observation.get("opponent_position")
                if opp is not None:
                    ox, oy = opp
                    score = -(abs(nx - ox) + abs(ny - oy))
                else:
                    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                    score = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if score > best or (score == best and (dx, dy) < candidates[0] if candidates else True):
                best = score
                candidates = [(dx, dy)]

    if not candidates:
        return [0, 0]
    return [int(candidates[0][0]), int(candidates[0][1])]