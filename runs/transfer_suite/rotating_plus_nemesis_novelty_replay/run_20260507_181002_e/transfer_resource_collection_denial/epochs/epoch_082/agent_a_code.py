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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny, dx, dy = sx, sy, 0, 0

        # choose the resource that maximizes one-step "claim advantage"
        local_best = -10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # prioritize winning the closer contest; break ties toward faster self progress
            val = (od - sd) * 1000 - sd + (0 if rx == nx and ry == ny else 0)
            # discourage moving into the opponent's immediate chase line
            if sd == 1 and dist(nx, ny, ox, oy) <= 2:
                val -= 20
            if val > local_best:
                local_best = val

        # slight tie-break: prefer not stepping away from current best resource direction
        if local_best > best_val:
            best_val = local_best
            best_move = [dx, dy]
        elif local_best == best_val:
            # deterministic tie-break: prefer moves that reduce distance to the closest resource
            cur_close = min(dist(sx, sy, rx, ry) for rx, ry in resources)
            nxt_close = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            if nxt_close < cur_close:
                best_move = [dx, dy]

    return best_move