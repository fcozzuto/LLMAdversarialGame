def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    tr = observation.get("turns_remaining", 0)
    rem_cnt = observation.get("remaining_resource_count", len(resources))
    few = (tr <= 6) or (rem_cnt <= 2)

    best = None
    best_val = None
    for r in resources:
        rx, ry = r[0], r[1]
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obstacles:
            continue
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Encourage grabbing before opponent; when late/few, bias to closest to self.
        val = (od - sd) * 4.0 - sd * (0.35 if not few else 0.10)
        if sd == 0:
            val += 50.0
        elif sd == 1:
            val += 8.0
        # Slight preference to keep options (avoid overly far targets).
        val -= 0.02 * (sd * sd)
        if best is None or val > best_val or (val == best_val and (rx, ry) < best):
            best_val = val
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Deterministic secondary ordering: iterate in fixed moves; compute score, take max.
    def step_score(nx, ny):
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            return -10**9
        ns = abs(tx - nx) + abs(ty - ny)
        # Keep opponent from getting much closer to the same target.
        no = abs(tx - ox) + abs(ty - oy)
        nd_op = abs(tx - nx) + abs(ty - ny)  # proxy if opponent followed us; small tie-break
        # Prefer reducing distance to target; also avoid making ourselves closer to opponent.
        opp_closer = dist((nx, ny), (ox, oy)) - dist((sx, sy), (ox, oy))
        return (-(ns)) * 2.2 + (0.25 if (ns <= 1) else 0.0) - 0.05 * nd_op + 0.03 * (-opp_closer)

    best_move = (0, 0)
    best_ms = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ms = step_score(nx, ny)
        if best_ms is None or ms > best_ms or (ms == best_ms and (dx, dy) < best_move):
            best_ms = ms
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]