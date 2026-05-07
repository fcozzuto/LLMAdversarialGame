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

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    res_sorted = sorted(resources)
    best_t = res_sorted[0]
    best_key = None

    for rx, ry in res_sorted:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        if rem <= 3:
            key = (sd, -od, rx, ry)
        else:
            # Race-wins first; if can't win, deny by picking where we are closest relative to opponent.
            win = 0 if sd <= od else 1
            key = (win, sd, (od - sd), -od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        nd = kdist(nx, ny, tx, ty)
        curd = kdist(sx, sy, tx, ty)
        # Prefer progress to target; tie-break toward moving away from opponent to reduce interference.
        opp_after = kdist(nx, ny, ox, oy)
        val = (nd, 0 if nd < curd else 1, -opp_after, nx, ny, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]