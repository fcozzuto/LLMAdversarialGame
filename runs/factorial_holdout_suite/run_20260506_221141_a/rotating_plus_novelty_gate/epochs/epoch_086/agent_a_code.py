def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def mhd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    best_selfd = 10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Lookahead-1: from next cell, choose the resource where we maximize lead over opponent.
        local_best = -10**18
        local_selfd = 10**9
        for rx, ry in resources:
            sd = mhd(nx, ny, rx, ry)
            od = mhd(ox, oy, rx, ry)
            lead = od - sd  # positive means we can arrive earlier (or tie)
            if lead > local_best or (lead == local_best and sd < local_selfd):
                local_best = lead
                local_selfd = sd

        # Prefer larger lead; then smaller distance to the best target; then fewer steps from current (tie-break).
        cur_dist = mhd(nx, ny, sx, sy)
        val = local_best * 1000 - local_selfd - cur_dist
        if val > best_val:
            best_val = val
            best_selfd = local_selfd
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]