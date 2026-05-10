def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    scores = observation.get("scores") or {}
    self_name = observation.get("self_name")
    my_score = 0.0
    opp_score = 0.0
    if self_name in scores:
        my_score = float(scores.get(self_name, 0.0))
        for k, v in scores.items():
            if k != self_name:
                opp_score = float(v)
                break
    else:
        vals = list(scores.values())
        if vals:
            my_score = float(sorted(vals)[-1])
            opp_score = float(sorted(vals)[0]) if len(vals) > 1 else 0.0

    behind = my_score < opp_score

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 1000 if not behind else 900
        if resources:
            dres = min(abs(nx - rx) + abs(ny - ry) for (rx, ry) in resources)
            val += (200 - dres) if not behind else (180 - dres)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        val += dist_opp * (2 if not behind else -1)

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = [dx, dy]

    if best is None:
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best