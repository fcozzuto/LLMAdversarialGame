def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Drift toward opponent while respecting obstacles (keeps motion purposeful).
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            self_d = abs(nx - ox) + abs(ny - oy)
            if self_d < best[0] or (self_d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (self_d, dx, dy)
        return [int(best[1]), int(best[2])]

    # Pick a resource we can reach sooner than the opponent (or deny by maximizing lead).
    best_res = None
    best_key = None
    for rx, ry in resources:
        self_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        lead = opp_d - self_d
        key = (lead, -self_d, -((rx + ry) % 2), rx, ry)  # deterministic tie-breakers
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res

    # Greedy step toward target with obstacle avoidance; tie-break deterministically.
    best_step = None
    best_step_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        # Move that keeps/extends lead over opponent to the same target.
        self_after = abs(rx - nx) + abs(ry - ny)
        opp_after = abs(rx - ox) + abs(ry - oy)
        lead_after = opp_after - self_after
        key = (lead_after, -self_after, dx, dy)
        if best_step_key is None or key > best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]