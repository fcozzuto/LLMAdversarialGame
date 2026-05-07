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

    def mhd(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # Evaluate each move by the best "capture advantage" it enables (self earlier than opponent),
    # plus a small tie-break for being closer to any remaining resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in blocked:
            continue

        best_adv = -10**18
        best_dist = 10**9
        for rx, ry in resources:
            sd = mhd(nx, ny, rx, ry)
            od = mhd(ox, oy, rx, ry)
            adv = od - sd  # positive if we can reach sooner
            if adv > best_adv:
                best_adv = adv
            dist = sd
            if dist < best_dist:
                best_dist = dist

        # If we can't be earlier on any resource, still prefer moves that reduce our lead loss
        # deterministically via best_adv, and slightly prefer closer resources.
        val = best_adv * 100 - best_dist
        # Additional anti-stall: prefer moving when an equal best_adv exists.
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move