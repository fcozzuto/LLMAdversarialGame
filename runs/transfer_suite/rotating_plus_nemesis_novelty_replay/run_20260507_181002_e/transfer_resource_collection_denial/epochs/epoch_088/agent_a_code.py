def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_target():
        # Prefer resources we can reach "ahead" of opponent: (opp_d - self_d) large.
        # Deterministic tie-break: then by our distance, then lexicographic.
        scored = []
        for (x, y) in resources:
            sd = man(sx, sy, x, y)
            od = man(ox, oy, x, y)
            lead = od - sd
            scored.append((lead, -sd, x, y, sd, od))
        scored.sort(reverse=True)
        return scored[0]  # (lead, -sd, x, y, sd, od)

    target = best_target()
    tx, ty = target[2], target[3]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Local greedy: pick move that reduces our distance to target, with obstacle penalty.
    best_move = (10**9, 0, 0)  # (score, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        sd_next = man(nx, ny, tx, ty)
        od_now = man(ox, oy, tx, ty)
        # If opponent is very close to same target, also try to increase their distance.
        od_next = man(ox, oy, tx, ty)
        # (od_next - sd_next) higher is good; add small distance-to-target shaping.
        score = (-sd_next + (od_next - sd_next) * 0.1)  # deterministic float-like via ints below
        # Convert to integer-like ordering: scale to avoid float issues
        score_i = (-(sd_next * 10) + (od_now - sd_next))
        # Tie-break with coordinate order to keep deterministic
        if score_i < best_move[0]:
            best_move = (score_i, dx, dy)

    if best_move[0] == 10**9:
        return [0, 0]
    return [best_move[1], best_move[2]]