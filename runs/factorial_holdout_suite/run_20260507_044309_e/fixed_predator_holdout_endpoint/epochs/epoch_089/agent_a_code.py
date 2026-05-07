def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources") or []
    turns_remaining = int(observation.get("turns_remaining") or 0)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick target with a "contest-aware" heuristic:
    # - Prefer resources where we are earlier than opponent
    # - If we are not earlier, prefer resources far from opponent to reduce denial efficiency
    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)

        # If unreachable for us, heavily penalize
        if sd > turns_remaining + 1:
            continue

        # Contest penalty if opponent can arrive very close in time
        contest = 1 if od <= sd + 1 else 0
        opp_dist = max(abs(ox - rx), abs(oy - ry))
        # Deterministic tie-breakers: prefer higher opp_dist, then lower rx, then lower ry
        key = (contest, sd, -opp_dist, rx, ry, od - sd)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        rx, ry = int(resources[0][0]), int(resources[0][1])
    else:
        rx, ry = best

    # Choose step that improves approach to target, avoids obstacles, and keeps away from opponent
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = None
    best_step_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        self_to = man(nx, ny, rx, ry)
        opp_away = max(abs(nx - ox), abs(ny - oy))
        # Prefer smaller self_to; if tie, prefer moving away from opponent; if still tie, deterministic order
        key = (self_to, -opp_away, dx, dy)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = [dx, dy]

    if best_step is None:
        # Fallback: never step onto obstacle
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                best_step = [dx, dy]
                break
        if best_step is None:
            best_step = [0, 0]
    return best_step