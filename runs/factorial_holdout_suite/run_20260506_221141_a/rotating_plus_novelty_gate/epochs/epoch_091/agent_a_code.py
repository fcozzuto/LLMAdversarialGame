def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_sorted = sorted(resources)
    best = res_sorted[0]
    best_val = -10**18
    # Prefer resources we can arrive at no later than opponent; otherwise smallest slack loss.
    for rx, ry in res_sorted:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        if sd <= od:
            val = 10**6 + (od - sd)  # win the race
        else:
            val = (od - sd)  # less negative is better
        # Small secondary bias to reduce risk with sweep-row opponents: prefer lower y then higher x
        val += -(ry * 2) + (rx * 0.001)
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic order: already fixed deltas; evaluate by distance-to-target then tie by delta index
    best_move = [0, 0]
    best_d = 10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d = kdist(nx, ny, tx, ty)
        if d < best_d:
            best_d = d
            best_move = [dx, dy]
        elif d == best_d:
            # tie-break: prefer moves that change both coords (more direct) then lexicographic
            score = (1 if dx != 0 and dy != 0 else 0, -abs(dx), -abs(dy))
            cur_score = (1 if best_move[0] != 0 and best_move[1] != 0 else 0, -abs(best_move[0]), -abs(best_move[1]))
            if score > cur_score:
                best_move = [dx, dy]
    return best_move